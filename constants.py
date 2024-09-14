import os
import time
import logging
import argparse
import itertools
import sys

COURSE_URL = "https://udemy.com/api-2.0/courses/{course_id}/"
CURRICULUM_URL = "https://udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/?page_size=200"
LECTURE_URL = "https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}?fields[lecture]=asset,description,download_url,is_free,last_watched_second&fields[asset]=asset_type,media_sources,captions"
QUIZ_URL = "https://udemy.com/api-2.0/quizzes/{quiz_id}/assessments/?version=1&page_size=200&fields[assessment]=id,assessment_type,prompt,correct_response,section,question_plain,related_lectures"

HOME_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(HOME_DIR, "courses")

LOG_DIR = os.path.join(HOME_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f"{time.strftime('%Y-%m-%d')}.log")

class LogFormatter(logging.Formatter):
    RESET = "\x1b[0m"
    COLOR_CODES = {
        'INFO': "\x1b[32m",    # Green
        'WARNING': "\x1b[33m", # Yellow
        'ERROR': "\x1b[31m",   # Red
        'CRITICAL': "\x1b[41m" # Red background
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
console_handler.setFormatter(LogFormatter('%(asctime)s %(levelname)s : %(message)s'))
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s : %(message)s'))
logger.addHandler(file_handler)

class LoadAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Set the value to True if no argument is provided, otherwise set it to the string value.
        setattr(namespace, self.dest, values if values is not None else True)


# The animation function
def animate(stop_event, message, completed_message):
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if stop_event.is_set():
            break
        sys.stdout.write(f'\r{message} {c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f'\r{completed_message}             \n')