"""Обработка входа, сохранение ответов, проверка периодичности."""

import logging
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.employee import Employee, Department
from ...models.staff_status import StaffStatus
from ...schemas.auth import LoginRequest, LoginResponse
from ...schemas.assessment import SubmitAnswersRequest, AssessmentResult
from pydantic import BaseModel

from psych_analyzer import calculate_score, get_status, RETEST_PERIOD_DAYS

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.full_name == body.full_name).first()
    if emp is None or emp.password != body.password:
        raise HTTPException(status_code=401, detail="Неверные данные")
    return LoginResponse(emp_id=emp.id, full_name=emp.full_name, role="employee")


@router.post("/submit", response_model=AssessmentResult)
def submit_answers(body: SubmitAnswersRequest, db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=RETEST_PERIOD_DAYS)
    recent = (
        db.query(StaffStatus)
        .filter(StaffStatus.emp_id == body.emp_id, StaffStatus.date_passed >= cutoff)
        .first()
    )
    if recent:
        raise HTTPException(
            status_code=429,
            detail=f"Тест можно проходить раз в {RETEST_PERIOD_DAYS} дней.",
        )

    try:
        score = calculate_score(body.answers, body.consistency_pairs)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    result = get_status(score)

    record = StaffStatus(
        emp_id=body.emp_id,
        total_points=score,
        status=result["label"],
        advice=result["advice"],
    )
    db.add(record)
    db.commit()

    if result["label"] == "Нужна беседа":
        _send_alert(body.emp_id, score)

    return AssessmentResult(
        emp_id=body.emp_id,
        total_points=score,
        status=result["label"],
        advice=result["advice"],
    )


@router.get("/reminder/{emp_id}")
def get_reminder(emp_id: int, db: Session = Depends(get_db)):
    """Проверяет, пора ли сотруднику пройти тест, и возвращает мотивирующее сообщение."""
    last = (
        db.query(StaffStatus)
        .filter(StaffStatus.emp_id == emp_id)
        .order_by(StaffStatus.date_passed.desc())
        .first()
    )

    if last is None:
        return {
            "due": True,
            "days_left": 0,
            "message": "Вы ещё не проходили тест. Пройдите его сейчас — это займёт всего пару минут!",
        }

    days_since = (datetime.utcnow() - last.date_passed).days
    days_left = max(0, RETEST_PERIOD_DAYS - days_since)

    if days_left == 0:
        days_overdue = days_since - RETEST_PERIOD_DAYS
        if days_overdue >= 7:
            _send_alert(emp_id, score=-1)
            return {
                "due": True,
                "days_left": 0,
                "message": (
                    f"Вы не проходили тест уже {days_since} дней. "
                    "Ваш психолог уже ждёт результатов — пройдите тест прямо сейчас!"
                ),
            }
        return {
            "due": True,
            "days_left": 0,
            "message": "Срок прохождения теста истёк. Пожалуйста, пройдите его сейчас — это важно для вас и команды!",
        }

    return {
        "due": False,
        "days_left": days_left,
        "message": f"Следующий тест через {days_left} дн. Вы молодец, что следите за своим состоянием",
    }


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    rows = (
        db.query(StaffStatus, Employee)
        .join(Employee, StaffStatus.emp_id == Employee.id)
        .order_by(StaffStatus.date_passed.desc())
        .all()
    )
    return [
        {
            "emp_id": s.emp_id,
            "full_name": e.full_name,
            "total_points": s.total_points,
            "status": s.status,
            "advice": s.advice,
            "date_passed": s.date_passed.isoformat(),
        }
        for s, e in rows
    ]



@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    """Список отделов для формы добавления сотрудника."""
    depts = db.query(Department).order_by(Department.title).all()
    return [{"id": d.id, "title": d.title} for d in depts]


class AddEmployeeRequest(BaseModel):
    full_name: str
    position: str
    dept_id: int
    password: str


@router.post("/employees", status_code=201)
def add_employee(body: AddEmployeeRequest, db: Session = Depends(get_db)):
    """Добавить нового сотрудника — только для менеджера."""
    emp = Employee(
        full_name=body.full_name,
        position=body.position,
        dept_id=body.dept_id,
        password=body.password,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return {"id": emp.id, "full_name": emp.full_name}


def _send_alert(emp_id: int, score: int) -> None:
    import httpx

    url = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification_service:8002")
    try:
        resp = httpx.post(
            f"{url}/alert",
            json={"emp_id": emp_id, "score": score},
            timeout=2,
        )
        resp.raise_for_status()
    except httpx.TimeoutException:
        logging.warning("notification_service timeout for emp_id=%s", emp_id)
    except httpx.HTTPStatusError as e:
        logging.warning("notification_service returned %s for emp_id=%s", e.response.status_code, emp_id)
    except Exception as e:
        logging.warning("notification_service unreachable: %s", e)