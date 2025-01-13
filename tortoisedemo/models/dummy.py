
"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 09:03:01
LastEditors: zhai
LastEditTime: 2024-06-09 08:43:23
"""

from datetime import datetime
from tortoise import fields
from tortoisedemo.base import BaseModel


class DummyModel(BaseModel):
    """记录表"""

    name = fields.CharField(max_length=255, null=False)
    age = fields.IntField()
    salary = fields.FloatField()
    is_active = fields.BooleanField(default=True)
    birthdate = fields.DateField()
    created_at = fields.DatetimeField()
    notes = fields.TextField()
    json_data = fields.JSONField(null=True, default=None)

    class Meta:
        table = "dummy"


class DepartmentModel(BaseModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    factor = fields.FloatField()

    class Meta:
        table = "department"


class TeamModel(BaseModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

    class Meta:
        table = "team"


class EmployeeModel(BaseModel):
    id = fields.IntField(pk=True)
    number = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255)
    retire = fields.BooleanField(default=False)
    retire_date = fields.DatetimeField(default=datetime.now)
    department = fields.ForeignKeyField(
        "models.DepartmentModel", related_name="employees", null=True
    )
    teams = fields.ManyToManyField("models.TeamModel", related_name="members")

    class Meta:
        table = "employee"
