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
from tortoise.contrib.fastapi import register_tortoise





# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # app startup
#     async with register_tortoise(
#         app,
#         db_url="sqlite://tortoise.sqlite3",
#         modules={"models": ["tortoisedemo.models"]},
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
    app,
    db_url="sqlite://tortoise.sqlite3",
    modules={"models": ["tortoisedemo.models.dummy"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

from tortoisedemo.api.dummy.views import dummy_router

app.include_router(dummy_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='test_tortoise_router:app', host="127.0.0.1", port=8010, reload=True)