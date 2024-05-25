from typing import Union

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel

from crud.tortoise import TortoiseCRUDRouter
from tortoise.contrib.fastapi import register_tortoise

from models import PotatoModel




class Potato(BaseModel):
    id: int
    color: str
    mass: float
    thickness: float
    type: str



# class ORMModel(BaseModel):
#     id: int

#     class Config:
#         orm_mode = True


# class PotatoCreate(BaseModel):
#     thickness: float
#     mass: float
#     color: str
#     type: str


# class Potato(PotatoCreate, ORMModel):
#     pass


# TORTOISE_ORM = {
#     "connections": {"default": "sqlite://db.sqlite3"},
#     "apps": {
#         "models": {
#             "models": ["tests.implementations.tortoise_"],
#             "default_connection": "default",
#         },
#     },
# }



# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # app startup
#     async with register_tortoise(
#         app,
#         db_url="sqlite://:memory:",
#         modules={"models": ["models"]},
#         generate_schemas=True,
#         add_exception_handlers=True,
#     ):
#         # db connected
#         yield
#         # app teardown
#     # db connections closed




# app = FastAPI(title="FastapiCrudPro", lifespan=lifespan)
app = FastAPI(title="FastapiCrudPro")

register_tortoise(
    app=app,
    db_url='sqlite://db.sqlite',
    modules={'models': ['models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



router = TortoiseCRUDRouter(schema=Potato, db_model=PotatoModel)

# @router.get('')
# def overloaded_get_all():
#     return 'My overloaded route that returns all the items'

# @router.get('/{item_id}')
# def overloaded_get_one():
#     return 'My overloaded route that returns one item'

app.include_router(router)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', host="127.0.0.1", port=8010, reload=True)