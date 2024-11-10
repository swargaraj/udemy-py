import logging

from lib.constants import LOG_FILE_PATH


class LogFormatter(logging.Formatter):
    RESET = "\x1b[0m"
    COLOR_CODES = {
        "INFO": "\x1b[32m",
        "WARNING": "\x1b[33m",
        "ERROR": "\x1b[31m",
        "CRITICAL": "\x1b[41m",
    }

    def format(self, record):
        original_levelname = record.levelname

        log_color = self.COLOR_CODES.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"

        formatted_message = super().format(record)
        record.levelname = original_levelname

        return formatted_message


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LogFormatter("%(asctime)s %(levelname)s : %(message)s"))
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s : %(message)s"))
logger.addHandler(file_handler)
