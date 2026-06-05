"""Сервис уведомлений: приём алертов и список для психолога."""

import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = os.getenv("NOTIFICATION_DB_URL", "sqlite:////data/notifications.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    emp_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="notification_service", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AlertRequest(BaseModel):
    emp_id: int
    score: int


@app.post("/alert", status_code=202)
def receive_alert(body: AlertRequest, db: Session = Depends(get_db)):
    message = f"Сотрудник #{body.emp_id} набрал {body.score} баллов — требуется беседа."
    alert = Alert(emp_id=body.emp_id, score=body.score, message=message)
    db.add(alert)
    db.commit()
    print(f"[ALERT] {message}", flush=True)
    return {"status": "logged", "alert_id": alert.id}


@app.get("/alerts")
def list_alerts(unread_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(Alert)
    if unread_only:
        query = query.filter(Alert.is_read == False)
    rows = query.order_by(Alert.created_at.desc()).all()
    return [
        {
            "id": a.id,
            "emp_id": a.emp_id,
            "score": a.score,
            "message": a.message,
            "created_at": a.created_at.isoformat(),
            "is_read": a.is_read,
        }
        for a in rows
    ]


@app.post("/alerts/{alert_id}/read")
def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert is None:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    alert.is_read = True
    db.commit()
    return {"id": alert.id, "is_read": True}


@app.get("/health")
def health():
    return {"status": "ok"}
