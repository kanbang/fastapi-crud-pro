from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional


class DummyCreateDTO(BaseModel):
    name: str
    age: int
    salary: float
    is_active: bool
    birthdate: date
    created_at: datetime
    notes: str
    json_data: object


class DummyDTO(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    age: Optional[int] = None
    salary: Optional[float] = None
    is_active: Optional[bool] = None
    birthdate: Optional[date] = None
    created_at: Optional[datetime] = None
    notes: Optional[str] = None
    json_data: Optional[object] = None

    # V2
    model_config = ConfigDict(from_attributes=True)

    # V1
    # class Config:
    #     orm_mode = True
    #     from_attributes
