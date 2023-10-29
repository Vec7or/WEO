from exceptions.WeoError import WeoError


class EnvironmentNotFoundError(WeoError):
    def __init__(self, message="A environment with that name could not be found"):
        super().__init__(message)
