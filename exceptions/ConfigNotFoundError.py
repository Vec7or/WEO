from exceptions.WeoError import WeoError


class ConfigNotFoundError(WeoError):
    def __init__(self, message="The requested config could not be found"):
        super().__init__(message)
