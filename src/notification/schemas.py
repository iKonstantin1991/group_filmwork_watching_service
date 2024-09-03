from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    EMAIL = "email"
    WEBSOCKET = "websocket"
    SMS = "sms"
    PUSH = "push"


class NotificationType(str, Enum):
    CREATED_RESERVATION = "group_filmwork_watching.created_reservation"
    CANCELLED_RESERVATION = "group_filmwork_watching.cancelled_reservation"


class Notification(BaseModel):
    notification_type: NotificationType
    send_at: datetime | None = None
    recipients: list[UUID]
    channels: list[ChannelType]
    template_vars: dict[Any, Any]
    template_id: UUID | None = None
    group_id: UUID = Field(default_factory=uuid4)
