from exceptions.WeoError import WeoError


class ImageNotSupportedError(WeoError):
    def __init__(self, message="WEO is not able to provision the given docker image"):
        super().__init__(message)
