from enum import Enum


class WatchStatus(str, Enum):
    CREATED = "created"
    CLOSED = "closed"
