from enum import Enum

from src.config import settings


class ChannelType(str, Enum):
    EMAIL = "email"
    WEBSOCKET = "websocket"
    SMS = "sms"
    PUSH = "push"


class NotificationType(str, Enum):
    COMPLETED_RESERVATION = "group_filmwork_watching.created_reservation"
    CANCELLED_RESERVATION = "group_filmwork_watching.cancelled_reservation"


class NotificationTemplateId(Enum):
    COMPLETED_RESERVATION = settings.template_id_completed_reservation
    CANCELLED_RESERVATION = settings.template_id_cancelled_reservation
