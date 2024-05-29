'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 09:03:01
LastEditors: zhai
LastEditTime: 2024-05-29 13:45:50
'''
from tortoise import Model, fields
from datetime import datetime

class BaseModel(Model):
    """Base for all models."""

    id = fields.IntField(pk=True)
    creation_date = fields.DatetimeField(auto_now_add=True, description="创建时间")
    created_by = fields.IntField(null=True, description="创建人ID")
    updation_date = fields.DatetimeField(auto_now=True, description="更新时间")
    updated_by = fields.IntField(null=True, description="更新人ID")
    enabled_flag = fields.BooleanField(default=True, description="是否删除, 0 删除 1 非删除")
    trace_id = fields.CharField(max_length=255, null=True, description="trace_id")

    class Meta:
        abstract = True
        table_description = "Base model with common fields"
        table_args = {
            "charset": "utf8"
        }
        
class PotatoModel(BaseModel):
    thickness = fields.FloatField()
    mass = fields.FloatField()
    color = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)


class CarrotModel(BaseModel):
    length = fields.FloatField()
    color = fields.CharField(max_length=255)


class DepartmentModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    factor = fields.FloatField()
    employees = fields.ReverseRelation["EmployeeModel"]

    class Meta:
        table = "department"


class TeamModel(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    employees = fields.ManyToManyField(
        "models.EmployeeModel", related_name="teams", through="team_employee"
    )

    class Meta:
        table = "team"


class EmployeeModel(Model):
    id = fields.IntField(pk=True)
    number = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255)
    retire = fields.BooleanField(default=False)
    retire_date = fields.DatetimeField(default=datetime.now)
    department = fields.ForeignKeyField(
        "models.DepartmentModel", related_name="employees", null=True
    )
    teams = fields.ManyToManyField(
        "models.TeamModel", related_name="members", through="team_employee"
    )

    class Meta:
        table = "employee"


# Association table for many-to-many relationship between teams and employees
class TeamEmployee(Model):
    team = fields.ForeignKeyField("models.TeamModel", on_delete=fields.CASCADE)
    employee = fields.ForeignKeyField("models.EmployeeModel", on_delete=fields.CASCADE)

    class Meta:
        table = "team_employee"
        unique_together = (("team", "employee"),)