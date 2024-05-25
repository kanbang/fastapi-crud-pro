'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-13 21:28:13
LastEditors: zhai
LastEditTime: 2024-05-25 18:58:44
'''
"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-13 15:56:19
LastEditors: zhai
LastEditTime: 2023-08-13 21:44:15
"""


from crud.sqlalchemy_crud import SQLAlchemyCRUDRouter
from sqlalchemydemo.db import get_db_session
from sqlalchemydemo.api.relation.schema import DepartmentCreateDTO, DepartmentDTO, EmployeeCreateDTO, EmployeeDTO, TeamCreateDTO, TeamDTO
from sqlalchemydemo.models.relation import DepartmentModel, EmployeeModel, TeamModel


employee_router = SQLAlchemyCRUDRouter(
    schema=EmployeeDTO,
    create_schema=EmployeeCreateDTO,
    db_model=EmployeeModel,
    db=get_db_session,
    prefix="employee",
)

team_router = SQLAlchemyCRUDRouter(
    schema=TeamDTO,
    create_schema=TeamCreateDTO,
    db_model=TeamModel,
    db=get_db_session,
    prefix="team",
)

department_router = SQLAlchemyCRUDRouter(
    schema=DepartmentDTO,
    create_schema=DepartmentCreateDTO,
    db_model=DepartmentModel,
    db=get_db_session,
    prefix="department",
)


# @router.post("/custom_router")
# async def test(para1: int, para2: str, session: AsyncSession = Depends(get_db_session)):
#     return resp_success(data="test custom router")
