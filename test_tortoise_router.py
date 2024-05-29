'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 21:37:06
LastEditors: zhai
LastEditTime: 2024-05-25 21:42:30
'''
from typing import Union

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel

from crud.tortoise_crud import TortoiseCRUDRouter
from tortoise.contrib.fastapi import register_tortoise

# from sqlalchemydemo.db import create_db
from tortoisedemo.models import PotatoModel


class Potato(BaseModel):
    id: int
    color: str
    mass: float
    thickness: float
    type: str



@asynccontextmanager
async def lifespan(app: FastAPI):
    # app startup
    async with register_tortoise(
        app,
        db_url="sqlite://:memory:",
        modules={"models": ["models"]},
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        # db connected
        yield
        # app teardown
    # db connections closed

app = FastAPI(title="FastapiCrudPro", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', host="127.0.0.1", port=8010, reload=True)