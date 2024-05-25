'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-09 23:17:04
LastEditors: zhai
LastEditTime: 2024-05-25 19:00:41
'''
"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-09 23:17:04
LastEditors: zhai
LastEditTime: 2023-08-09 23:18:11
"""
"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-07-29 09:04:46
LastEditors: zhai
LastEditTime: 2023-07-29 09:10:22
"""
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    Text,
    JSON,
)

from datetime import datetime, date

from sqlalchemydemo.base import Base


class DummyModel(Base):
    """记录表"""

    __tablename__ = "dummy"

    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    salary: Mapped[float] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    birthdate: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    notes: Mapped[str] = mapped_column(Text)
    json_data: Mapped[object] = mapped_column(JSON, nullable=True)

