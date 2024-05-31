'''
Descripttion: 
version: 0.x
Author: zhai
Date: 2024-05-25 09:03:01
LastEditors: zhai
LastEditTime: 2024-05-25 20:53:40
'''
from enum import Enum
from typing import Dict, Generic, TypeVar, Optional, Sequence

from fastapi.params import Depends
from pydantic import BaseModel

PAGINATION = Dict[str, Optional[int]]
PYDANTIC_SCHEMA = BaseModel

T = TypeVar("T", bound=BaseModel)
DEPENDENCIES = Optional[Sequence[Depends]]

#########################################################################
class UserDataFilter(str, Enum):
    ALL_DATA = "ALL_DATA"
    SELF_DATA = "SELF_DATA"

class UserDataFilterAll(str, Enum):
    ALL_DATA = "ALL_DATA"
    
class UserDataFilterSelf(str, Enum):
    SELF_DATA = "SELF_DATA"


class UserDataOption(str, Enum):
    ALL_ONLY = "ALL_ONLY"
    ALL_DEFAULT = "ALL_DEFAULT"
    SELF_ONLY = "SELF_ONLY"
    SELF_DEFAULT = "SELF_DEFAULT"

#########################################################################
class RespModelT(BaseModel, Generic[T]):
    code: int
    msg: str
    data: T
    success: bool
    trace_id: Optional[str]

#########################################################################
class IdNotExist(Exception):
    def __init__(self):
        super().__init__("id不存在")


class InvalidQueryException(Exception):
    def __init__(self):
        super().__init__("invalid query")


