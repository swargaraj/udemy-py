import os
import re
import subprocess
import sys

from lib.logger import logger


def check_prerequisites(cookie_path):
    if not os.path.isfile(cookie_path):
        logger.error("The provided cookie file path does not exist.")

    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError:
        logger.error("ffmpeg is not installed or not found in the system PATH.")
        sys.exit(1)

    try:
        subprocess.run(
            ["n_m3u8dl-re", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError:
        logger.error(
            "Make sure mp4decrypt & n_m3u8dl-re is not installed or not found in the system PATH."
        )
        sys.exit(1)

    return True


def remove_emojis_and_binary(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed Characters
        "]+",
        flags=re.UNICODE,
    )

    text = emoji_pattern.sub(r"", text)

    text = "".join(c for c in text if 32 <= ord(c) <= 126)

    return text


def timestamp_to_seconds(timestamp):
    hours, minutes, seconds = timestamp.split(":")
    seconds, fraction = seconds.split(".")
    total_seconds = (
        int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(fraction) / 100
    )
    return total_seconds


def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (
        f"{hours}hr {minutes}min {seconds}s"
        if hours > 0
        else f"{minutes}min {seconds}s"
    )


def is_valid_chapter(mindex, start_chapter, end_chapter):
    return start_chapter <= mindex <= end_chapter


def is_valid_lecture(
    mindex, lindex, start_chapter, start_lecture, end_chapter, end_lecture
):
    if mindex == start_chapter and lindex < start_lecture:
        return False
    if mindex == end_chapter and lindex > end_lecture:
        return False
    return True


def validate_concurrent_downloads(concurrent):
    if concurrent > 25:
        logger.warning(
            "The maximum number of concurrent downloads is 25. Capping to 25."
        )
        return 25
    elif concurrent < 1:
        logger.warning("The minimum number of concurrent downloads is 1. Capping to 1.")
        return 1
    return concurrent


def determine_course_id(args, udemy, course_url):
    if args.id:
        return args.id
    elif course_url:
        return udemy.extract_course_id(course_url)
    else:
        logger.error(
            "You must provide either the course ID with '--id' or the course URL with '--url'."
        )
        sys.exit(1)
