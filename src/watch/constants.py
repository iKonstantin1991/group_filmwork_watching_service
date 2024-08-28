from enum import Enum


class WatchStatus(str, Enum):
    CREATED = "created"
    CANCELLED = "cancelled"
