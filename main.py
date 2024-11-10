"""
Udemy Downloader

A Python-based tool that allows users to download Udemy course content
and save it locally for offline access. It fetches course videos, assets,
other materials, by interacting with the Udemy API.

Basic Usage:
    python main.py --course-url <URL> --cookie <PATH>

Author: Swargaraj
GitHub: https://github.com/swargaraj/udemy-py
"""

import json
import os
import sys
import time

from pathvalidate import sanitize_filename
import requests
from rich import print as rprint
from rich.console import Console
from rich.tree import Tree

from lib import udemy as udemy_client
from lib.constants import DOWNLOAD_DIR, HOME_DIR
from lib.data_classes import DownloadSettings, UdemySettings
from lib.helpers import (
    check_prerequisites,
    determine_course_id,
    format_time,
    remove_emojis_and_binary,
    validate_concurrent_downloads,
)
from lib.logger import logger
from lib.parser import create_parser

console = Console()


def main():
    try:
        parser = create_parser()
        args = parser.parse_args()

        if len(sys.argv) == 1:
            print(parser.format_help())
            sys.exit(0)

        course_url = args.url
        key = args.key

        if not course_url and not args.id:
            logger.error(
                """You must provide either the course ID with '--id' or the course URL
                with '--url' to proceed."""
            )
            return

        if course_url and args.id:
            logger.warning(
                "Both course ID and URL provided. Prioritizing course ID over URL."
            )

        if key is not None and ":" not in key:
            logger.error(
                """The provided Widevine key is either malformed or incorrect.
                Please check the key and try again."""
            )
            sys.exit(1)

        portal = args.portal or "www"
        cookie_path = args.cookies or os.path.join(HOME_DIR, "cookies.txt")

        check_prerequisites(cookie_path)

        try:
            captions = args.captions.split(",") if args.captions else ["en_US"]
        except AttributeError:
            logger.critical("Captions must be a comma-separated list of locale IDs.")
            sys.exit(1)

        skip_captions = args.skip_captions
        skip_assets = args.skip_assets
        skip_lectures = args.skip_lectures
        skip_articles = args.skip_articles
        skip_assignments = args.skip_assignments
        max_concurrent_lectures = validate_concurrent_downloads(args.concurrent)

        udemy_settings = UdemySettings(
            course_url,
            key,
            portal,
            cookie_path,
            captions,
            skip_captions,
            skip_assets,
            skip_lectures,
            skip_articles,
            skip_assignments,
            bool(args.srt),
        )

        udemy = udemy_client.Udemy(udemy_settings)

        course_id = determine_course_id(args, udemy, course_url)

        course_info = udemy.fetch_course(course_id)
        COURSE_DIR = os.path.join(
            DOWNLOAD_DIR,
            remove_emojis_and_binary(sanitize_filename(course_info["title"])),
        )
        logger.info("Course Title: %s", course_info["title"])

        udemy.create_directory(COURSE_DIR)

        if args.load:
            load_path = (
                args.load
                if args.load is not True
                else os.path.join(HOME_DIR, "course.json")
            )

            if not os.path.isfile(load_path):
                logger.error(
                    """The course curriculum file could not be located at %s. Please verify the file path
                    and ensure that the file exists.""",
                    load_path,
                )
                sys.exit(1)

            try:
                with open(load_path, "r", encoding="utf-8") as file:
                    course_curriculum = json.load(file)
                    logger.info(
                        "The course curriculum has been successfully loaded from %s",
                        load_path,
                    )
            except json.JSONDecodeError:
                logger.error(
                    "The course curriculum file at %s is either malformed or corrupted.",
                    load_path,
                )
                sys.exit(1)

        else:
            try:
                course_curriculum = udemy.fetch_course_curriculum(course_id)
            except requests.exceptions.RequestException as e:
                logger.critical("Unable to retrieve the course curriculum: %s", e)
                sys.exit(1)
            except json.JSONDecodeError as e:
                logger.critical(
                    "Invalid JSON received while retrieving course curriculum: %s", e
                )
                sys.exit(1)

        save_path = (
            args.save
            if args.save is not True
            else os.path.join(HOME_DIR, "course.json")
        )

        if os.path.isfile(save_path):
            logger.warning(
                """Course curriculum file already exists at %s.
                           Overwriting the existing file.""",
                save_path,
            )

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(course_curriculum, f, indent=4)

        logger.info(
            "The course curriculum has been successfully saved to %s", save_path
        )

        if args.tree:
            root_tree = Tree(course_info["title"], style="green")
            udemy.build_curriculum_tree(course_curriculum, root_tree)
            rprint(root_tree)

            if isinstance(args.tree, str):
                if os.path.isfile(args.tree):
                    logger.warning(
                        "Course Curriculum Tree file already exists. Overwriting the existing file."
                    )

                with open(args.tree, "w", encoding="utf-8") as f:
                    rprint(root_tree, file=f)
                    logger.info(
                        "The course curriculum tree has been successfully saved to %s",
                        args.tree,
                    )

        start_chapter = 0
        start_lecture = 0

        if args.start_lecture:
            if args.start_chapter is None:
                logger.error(
                    "When using --start-lecture please provide --start-chapter"
                )
                sys.exit(1)
            start_chapter = args.start_chapter
            start_lecture = args.start_lecture
        elif args.start_chapter:
            start_chapter = args.start_chapter

        end_chapter = len(course_curriculum)
        end_lecture = 1000

        if args.end_lecture:
            if not args.end_chapter:
                logger.error("When using --end-lecture please provide --end-chapter")
                sys.exit(1)
            end_chapter = args.end_chapter
            end_lecture = args.end_lecture
        elif args.end_chapter:
            end_chapter = args.end_chapter
            end_lecture = 1000

        logger.info(
            "The course download is starting. Please wait while the materials are being downloaded."
        )

        settings = DownloadSettings(
            max_concurrent_lectures=max_concurrent_lectures,
            start_chapter=start_chapter,
            end_chapter=end_chapter,
            start_lecture=start_lecture,
            end_lecture=end_lecture,
        )

        logger.info("Download started.")
        start_time = time.time()
        udemy.download_course(course_curriculum, settings)
        elapsed_time = time.time() - start_time
        logger.info("Download finished in %s", format_time(elapsed_time))
        logger.info("All course materials have been successfully downloaded.")

    except KeyboardInterrupt:
        logger.warning("Process interrupted. Exiting")
        sys.exit(1)


if __name__ == "__main__":
    main()
