from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class PlaceBase(BaseModel):
    name: str
    address: str


class PlaceCreate(PlaceBase):
    city: str


class Place(PlaceBase):
    id: UUID
    created_at: datetime
    host: UUID
    status: str
