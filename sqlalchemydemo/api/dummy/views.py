'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 19:05:58
LastEditors: zhai
LastEditTime: 2024-05-25 21:25:06
'''
'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-14 09:46:56
LastEditors: zhai
LastEditTime: 2023-12-23 15:01:20
'''
'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2023-08-13 15:56:19
LastEditors: zhai
LastEditTime: 2023-08-13 16:25:16
'''

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.sqlalchemy_crud import SQLAlchemyCRUDRouter
from sqlalchemydemo.api.dummy.schema import DummyCreateDTO, DummyDTO
from sqlalchemydemo.db import get_db_session
from sqlalchemydemo.models.dummy import DummyModel
from crud._types import UserDataOption
from crud._utils import resp_success


# Example query: [["age", ">=", "25"], ["name", "=", "Alice"]]


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# def token_auth(token: str = Depends(oauth2_scheme)):
#     print(token)
#     if not token:
#         raise HTTPException(401, "Invalid token")

# router = SQLAlchemyCRUDRouter(schema=DummyDTO, dependencies=[Depends(token_auth)])



dummy_router = SQLAlchemyCRUDRouter(
    schema=DummyDTO,
    create_schema=DummyCreateDTO,
    user_data_option=UserDataOption.SELF_DEFAULT,
    db_model=DummyModel,
    db=get_db_session,
    prefix="dummy",
)


@dummy_router.post("/custom_router")
async def test(
    para1: int,
    para2: str,
    session: AsyncSession = Depends(get_db_session)
):
    return resp_success(data="test custom router")


@dummy_router.get('')
def overloaded_get_all():
    return 'My overloaded route that returns all the items'

@dummy_router.get('/{item_id}')
def overloaded_get_one():
    return 'My overloaded route that returns one item'

