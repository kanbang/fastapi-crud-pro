'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 09:03:01
LastEditors: zhai
LastEditTime: 2024-05-25 21:38:30
'''
from typing import Union
from fastapi import FastAPI

from sqlalchemydemo.api.dummy.views import dummy_router
from sqlalchemydemo.api.relation.views import department_router, team_router, employee_router

app = FastAPI(title="FastapiCrudPro")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

app.include_router(dummy_router)

app.include_router(employee_router)
app.include_router(team_router)
app.include_router(department_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='test_sqlalchemy_router:app', host="127.0.0.1", port=8010, reload=True)