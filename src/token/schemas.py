from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class Role(str, Enum):
    SUBSCRIBER = "subscriber"
    ADMIN = "admin"
    SUPERUSER = "superuser"
    SERVICE = "service"


class User(BaseModel):
    id: UUID
    roles: list[str]
