class WatchBaseError(Exception):
    pass


class WatchPermissionError(WatchBaseError):
    pass


class WatchClosingError(WatchBaseError):
    pass


class WatchCreatingError(WatchBaseError):
    pass
