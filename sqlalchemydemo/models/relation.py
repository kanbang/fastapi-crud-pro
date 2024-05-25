'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-14 09:46:56
LastEditors: zhai
LastEditTime: 2024-05-25 12:20:35
'''
"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-13 20:23:03
LastEditors: zhai
LastEditTime: 2023-08-13 21:10:26
"""
from typing import List
from sqlalchemy import (
    Float,
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import  relationship
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemydemo.base import Base


class DepartmentModel(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    factor: Mapped[float] = mapped_column(Float)
    employees: Mapped[List["EmployeeModel"]] = relationship(back_populates="department")


teams_employee_table = Table(
    "association_table",
    Base.metadata,
    Column("team_id", ForeignKey("team.id"), primary_key=True),
    Column("employee_id", ForeignKey("employee.id"), primary_key=True),
)


class TeamModel(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    employees: Mapped[List["EmployeeModel"]] = relationship(
        secondary=teams_employee_table, back_populates="teams"
    )


class EmployeeModel(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    retire = mapped_column(Boolean, default=False)
    retire_date = mapped_column(DateTime, default=datetime.now)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("department.id"), nullable=True)
    department: Mapped[DepartmentModel] = relationship(
        "DepartmentModel", backref="demployees"
    )
    teams: Mapped[List[TeamModel]] = relationship(
        secondary=teams_employee_table, back_populates="employees"
    )
