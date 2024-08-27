from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Watch(BaseModel):
    id: UUID
    host: UUID
    filmwork_id: UUID
    place_id: UUID
    time: datetime
    seats: int
    price: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WatchCreate(BaseModel):
    host: UUID
    filmwork_id: UUID
    place_id: UUID
    time: datetime
    seats: int
    price: float

    model_config = ConfigDict(from_attributes=True)


class WatchFilters(BaseModel):
    host_id: UUID | None
    filmwork_id: UUID | None
    place_id: UUID | None
    watch_id: UUID | None
