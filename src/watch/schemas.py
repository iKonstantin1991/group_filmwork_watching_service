from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WatchBase(BaseModel):
    host: UUID
    filmwork_id: UUID
    place_id: UUID
    time: datetime
    seats: int
    price: float


class Watch(WatchBase):
    id: UUID
    price: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WatchWithAvailableSeats(WatchBase):
    id: UUID
    price: float
    status: str
    created_at: datetime
    available_seats: int


class WatchCreate(WatchBase):
    pass


class WatchFilters(BaseModel):
    host_id: UUID | None
    filmwork_id: UUID | None
    place_id: UUID | None
    watch_id: UUID | None
