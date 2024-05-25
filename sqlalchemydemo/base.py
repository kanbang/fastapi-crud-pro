'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 11:53:59
LastEditors: zhai
LastEditTime: 2024-05-25 13:39:07
'''
from datetime import datetime
from sqlalchemy import func, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Text, Integer, JSON, DateTime, Boolean


meta = MetaData()

class Base(DeclarativeBase):
    """Base for all models."""
    metadata = meta
  
    __table_args__ = {"mysql_charset": "utf8"}  # 设置表的字符集
    __mapper_args__ = {"eager_defaults": True}  # 防止 insert 插入后不刷新

    # @declared_attr
    # def __tablename__(cls) -> str:
    #     """将类名小写并转化为表名 __tablename__"""
    #     return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creation_date = mapped_column(DateTime(), default=func.now(), comment="创建时间")
    created_by: Mapped[int] = mapped_column(Integer, nullable=True, comment="创建人ID")
    updation_date: Mapped[datetime] = mapped_column(
        DateTime(),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )
    updated_by: Mapped[int] = mapped_column(Integer, nullable=True, comment="更新人ID")
    enabled_flag = mapped_column(
        Boolean(), default=1, nullable=False, comment="是否删除, 0 删除 1 非删除"
    )
    trace_id: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="trace_id"
    )

