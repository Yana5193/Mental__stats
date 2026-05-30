"""Таблица результатов"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from .base import Base

class StaffStatus(Base):
    __tablename__="staff_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    total_points = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    advice = Column(String, nullable=False)
    date_passed = Column(DateTime, default=datetime.utcnow, nullable=False)