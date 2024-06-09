'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-13 21:28:13
LastEditors: zhai
LastEditTime: 2024-06-09 09:04:30
'''
"""
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-13 15:56:19
LastEditors: zhai
LastEditTime: 2023-08-13 21:44:15
"""


from crud.tortoise_crud import TortoiseCRUDRouter
from tortoisedemo.api.relation.schema import DepartmentCreateDTO, DepartmentDTO, EmployeeCreateDTO, EmployeeDTO, TeamCreateDTO, TeamDTO
from tortoisedemo.models.dummy import DepartmentModel, EmployeeModel, TeamModel


employee_router = TortoiseCRUDRouter(
    schema=EmployeeDTO,
    create_schema=EmployeeCreateDTO,
    db_model=EmployeeModel,
    prefix="employee",
)

team_router = TortoiseCRUDRouter(
    schema=TeamDTO,
    create_schema=TeamCreateDTO,
    db_model=TeamModel,
    prefix="team",
)

department_router = TortoiseCRUDRouter(
    schema=DepartmentDTO,
    create_schema=DepartmentCreateDTO,
    db_model=DepartmentModel,
    prefix="department",
)


# @router.post("/custom_router")
# async def test(para1: int, para2: str, session: AsyncSession = Depends(get_db_session)):
#     return resp_success(data="test custom router")
