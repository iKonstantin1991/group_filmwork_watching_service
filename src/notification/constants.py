from enum import Enum


class ChannelType(str, Enum):
    EMAIL = "email"
    WEBSOCKET = "websocket"
    SMS = "sms"
    PUSH = "push"


class NotificationType(str, Enum):
    CREATED_RESERVATION = "group_filmwork_watching.created_reservation"
    CANCELLED_RESERVATION = "group_filmwork_watching.cancelled_reservation"
