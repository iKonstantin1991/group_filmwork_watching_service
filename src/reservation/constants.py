from enum import Enum


class ReservationStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    UNPAID = "unpaid"
    CANCELLED = "cancelled"
