"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-14 09:46:56
LastEditors: zhai
LastEditTime: 2023-08-14 10:20:04
"""
"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-13 21:28:13
LastEditors: zhai
LastEditTime: 2023-08-13 21:30:41
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import List, Optional


class EmployeeCreateDTO(BaseModel):
    number: str
    name: str
    retire: bool
    retire_date: datetime
    department_id: Optional[int] = None
    # department: Optional[DepartmentModel] = relationship(
    #     "DepartmentModel", backref="employees"
    # )
    # teams: Optional[List[TeamModel]] = relationship(
    #     secondary=teams_employee_table, back_populates="employees"
    # )


class Ref_DepartmentDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    factor: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class Ref_TeamDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

class EmployeeDTO(BaseModel):
    id: Optional[int] = None
    number: Optional[str] = None
    name: Optional[str] = None
    retire: Optional[bool] = None
    retire_date: Optional[datetime] = None
    department: Optional[Ref_DepartmentDTO] = None
    department_id: Optional[int] = None
    teams: Optional[List[Ref_TeamDTO]] = None
    teams_refids: Optional[List[int]] = None


    model_config = ConfigDict(from_attributes=True)

###################################################################################

class DepartmentCreateDTO(BaseModel):
    name: str
    factor: float


class DepartmentDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    factor: Optional[float] = None
    employees: Optional[List[EmployeeDTO]] = None
    employees_refids: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True)


###################################################################################


class TeamCreateDTO(BaseModel):
    name: str
    # employees


class TeamDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    employees: Optional[List[EmployeeDTO]] = None
    employees_refids: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True)




###################################################################################

# teams_employee_table = Table(
#     "association_table",
#     Base.metadata,
#     Column("team_id", ForeignKey("team.id"), primary_key=True),
#     Column("employee_id", ForeignKey("employee.id"), primary_key=True),
# )
