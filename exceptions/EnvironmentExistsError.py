from exceptions.WeoError import WeoError


class EnvironmentExistsError(WeoError):
    def __init__(self, message="A environment with that name already exists"):
        super().__init__(message)
