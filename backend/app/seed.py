"""Начальные данные: сотрудники и отделы."""

from .database import SessionLocal, create_tables
from .models.employee import Employee, Department


SEED_DEPARTMENTS = ["Разработка", "Маркетинг", "HR", "Финансы", "Поддержка"]

SEED_EMPLOYEES = [
    ("Иванова Анна Петровна",    "Разработчик",   "Разработка",  "pass001"),
    ("Смирнов Олег Игоревич",    "Тестировщик",   "Разработка",  "pass002"),
    ("Козлова Мария Сергеевна",  "Менеджер",      "Маркетинг",   "pass003"),
    ("Новиков Денис Андреевич",  "HR-специалист", "HR",          "pass004"),
    ("Попова Елена Витальевна",  "Аналитик",      "Финансы",     "pass005"),
    ("Соколов Артём Юрьевич",    "Инженер",       "Поддержка",   "pass006"),
    ("Волкова Юлия Романовна",   "Дизайнер",      "Маркетинг",   "pass007"),
    ("Морозов Кирилл Павлович",  "Разработчик",   "Разработка",  "pass008"),
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        if db.query(Employee).count() > 0:
            return  

        dept_map = {}
        for title in SEED_DEPARTMENTS:
            dept = Department(title=title)
            db.add(dept)
            db.flush()
            dept_map[title] = dept.id

        for full_name, position, dept_title, password in SEED_EMPLOYEES:
            db.add(Employee(
                full_name=full_name,
                position=position,
                dept_id=dept_map[dept_title],
                password=password,
            ))

        db.commit()
        print(f"Seed: добавлено {len(SEED_EMPLOYEES)} сотрудников.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()