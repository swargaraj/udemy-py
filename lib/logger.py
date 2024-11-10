import logging
from colorama import Fore, Back, Style, init
from lib.constants import LOG_FILE_PATH

init(autoreset=True)

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self.log(SUCCESS_LEVEL, message, *args, **kwargs)


logging.Logger.success = success


class LogFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.RESET = Style.RESET_ALL

    def format_label(self, label, bg_color):
        return f"{bg_color}{Style.BRIGHT}{Fore.WHITE} {label} {self.RESET}"

    def format(self, record):
        original_levelname = record.levelname

        level_colors = {
            "INFO": Back.BLUE,
            "SUCCESS": Back.GREEN,
            "WARNING": Back.YELLOW,
            "ERROR": Back.RED,
            "CRITICAL": Back.RED,
            "DEBUG": Back.CYAN,
        }

        bg_color = level_colors.get(record.levelname, "")
        record.levelname = self.format_label(record.levelname, bg_color)

        formatted_message = super().format(record)
        record.levelname = original_levelname

        return formatted_message


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LogFormatter("%(asctime)s %(levelname)s %(message)s", datefmt=DATE_FORMAT))
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt=DATE_FORMAT))
logger.addHandler(file_handler)
