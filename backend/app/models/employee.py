"""Модель аккаунта сотрудников"""
from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class Departament(Base):
    __tablename__="departments"

    id=Column(Integer,primary_key=True,autoincrement=True)
    tittle=Column(String,unique=True,nullable=True)

class Employee(Base):

    __tablename__="employees"

    id=Column(Integer,primary_key=True,autoincrement=True)
    full_name=Column(String,nullable=False)
    position=Column(String,nullable=False)
    dept_id=Column(Integer,ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    password=Column(String, nullable=False)