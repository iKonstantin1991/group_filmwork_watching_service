class ReservationBaseError(Exception):
    pass


class ReservationPermissionError(ReservationBaseError):
    pass


class ReservationMissingError(ReservationBaseError):
    pass


class ReservationPastWatchError(ReservationBaseError):
    pass


class ReservationMissingWatchError(ReservationBaseError):
    pass


class ReservationNotEnoughSeatsError(ReservationBaseError):
    pass
