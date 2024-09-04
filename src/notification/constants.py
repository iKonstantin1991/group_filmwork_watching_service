from enum import Enum
from uuid import UUID


class ChannelType(str, Enum):
    EMAIL = "email"
    WEBSOCKET = "websocket"
    SMS = "sms"
    PUSH = "push"


class NotificationType(str, Enum):
    COMPLETED_RESERVATION = "group_filmwork_watching.created_reservation"
    CANCELLED_RESERVATION = "group_filmwork_watching.cancelled_reservation"


class NotificationTemplateId(Enum):
    COMPLETED_RESERVATION = UUID("4b53be24-a687-4666-9513-ad4aa7da92a8")
    CANCELLED_RESERVATION = UUID("19f7a35d-ec6f-4c36-a01d-574c7c8aea35")
