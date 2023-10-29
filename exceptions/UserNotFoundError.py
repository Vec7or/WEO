from exceptions.WeoError import WeoError


class UserNotFoundError(WeoError):
    def __init__(self, message="The user provided does not exist within the image"):
        super().__init__(message)
