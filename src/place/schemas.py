from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceBase(BaseModel):
    name: str
    address: str


class PlaceCreate(PlaceBase):
    city: str


class Place(PlaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    host: UUID
    status: str
