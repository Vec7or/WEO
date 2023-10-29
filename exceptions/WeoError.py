class WeoError(Exception):
    def __init__(self, message="WEO encountered a problem"):
        super().__init__(message)
