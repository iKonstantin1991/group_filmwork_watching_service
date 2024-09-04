from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.notification.constants import ChannelType, NotificationTemplateId, NotificationType


class Notification(BaseModel):
    notification_type: NotificationType
    send_at: datetime | None = None
    recipients: list[UUID]
    channels: list[ChannelType]
    template_vars: dict[Any, Any]
    template_id: NotificationTemplateId | None = None
    group_id: UUID = Field(default_factory=uuid4)
