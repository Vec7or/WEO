from colorama import Fore, Style


class Logger:
    @staticmethod
    def start_info():
        print(Fore.LIGHTBLUE_EX, end="")


    @staticmethod
    def stop_info():
        print(Style.RESET_ALL)


    @staticmethod
    def info(msg: str):
        print(Fore.LIGHTBLUE_EX, end="")
        print(msg)
        print(Style.RESET_ALL)

    @staticmethod
    def warn(msg: str):
        print(Fore.YELLOW, end="")
        print(msg)
        print(Style.RESET_ALL)

    @staticmethod
    def err(msg: str):
        print(Fore.RED, end="")
        print(msg)
        print(Style.RESET_ALL)
