'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 09:03:01
LastEditors: zhai
LastEditTime: 2024-05-29 13:45:50
'''
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



# class DepartmentModel(Model):
#     id = fields.IntField(pk=True)
#     name = fields.CharField(max_length=255)
#     factor = fields.FloatField()
#     employees = fields.ReverseRelation["EmployeeModel"]

#     class Meta:
#         table = "department"


# class TeamModel(Model):
#     id = fields.IntField(pk=True)
#     name = fields.CharField(max_length=255)
#     employees = fields.ManyToManyField(
#         "models.EmployeeModel", related_name="teams", through="team_employee"
#     )

#     class Meta:
#         table = "team"


# class EmployeeModel(Model):
#     id = fields.IntField(pk=True)
#     number = fields.CharField(max_length=255, unique=True)
#     name = fields.CharField(max_length=255)
#     retire = fields.BooleanField(default=False)
#     retire_date = fields.DatetimeField(default=datetime.now)
#     department = fields.ForeignKeyField(
#         "models.DepartmentModel", related_name="employees", null=True
#     )
#     teams = fields.ManyToManyField(
#         "models.TeamModel", related_name="members", through="team_employee"
#     )

#     class Meta:
#         table = "employee"


# # Association table for many-to-many relationship between teams and employees
# class TeamEmployee(Model):
#     team = fields.ForeignKeyField("models.TeamModel", on_delete=fields.CASCADE)
#     employee = fields.ForeignKeyField("models.EmployeeModel", on_delete=fields.CASCADE)

#     class Meta:
#         table = "team_employee"
#         unique_together = (("team", "employee"),)