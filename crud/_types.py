from enum import Enum
from typing import Dict, Generic, Type, TypeVar, Optional, Sequence, Union, List

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



