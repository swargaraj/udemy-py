import http.cookiejar as cookielib
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from pathvalidate import sanitize_filename
from rich.live import Live
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.text import Text

from handlers.process_articles import download_article
from handlers.process_assets import download_supplementary_assets
from handlers.process_captions import download_captions
from handlers.process_m3u8 import download_and_merge_m3u8
from handlers.process_mp4 import download_mp4
from handlers.process_mpd import download_and_merge_mpd
from lib.constants import COURSE_URL, CURRICULUM_URL, LECTURE_URL
from lib.data_classes import DownloadSettings, UdemySettings
from lib.helpers import (
    format_time,
    is_valid_chapter,
    is_valid_lecture,
    remove_emojis_and_binary,
)
from lib.loader import ElapsedTimeColumn, Loader
from lib.logger import logger


class Udemy:
    def __init__(self, settings: UdemySettings):
        self.course_url = settings.course_url
        self.key = settings.key
        self.portal = settings.portal
        self.cookie_path = settings.cookie_path
        self.captions = settings.captions
        self.skip_captions = settings.skip_captions
        self.skip_assets = settings.skip_assets
        self.skip_lectures = settings.skip_lectures
        self.skip_articles = settings.skip_articles
        self.skip_assignments = settings.skip_assignments
        self.convert_to_srt = settings.convert_to_srt
        self.cookie_jar = None

        try:
            self.cookie_jar = cookielib.MozillaCookieJar(self.cookie_path)
            self.cookie_jar.load()
        except IOError:
            logger.critical(
                """The provided cookie file could not be read or is incorrectly
                formatted. Please ensure the file is in the correct format and
                contains valid authentication cookies."""
            )
            sys.exit(1)

    def request(self, url):
        try:
            response = requests.get(
                url, cookies=self.cookie_jar, stream=True, timeout=15
            )
            return response
        except requests.exceptions.RequestException:
            logger.critical(
                """There was a problem reaching the Udemy server.
                This could be due to network issues, an invalid URL,
                or Udemy being temporarily unavailable."""
            )
            return None

    def extract_course_id(self, course_url):

        with Loader("Fetching course ID"):
            response = self.request(course_url)
            content_str = response.content.decode("utf-8")

        meta_match = re.search(
            r'<meta\s+property="og:image"\s+content="([^"]+)"', content_str
        )

        if meta_match:
            url = meta_match.group(1)
            number_match = re.search(r"/(\d+)_", url)
            if number_match:
                number = number_match.group(1)
                logger.info("Course ID Extracted: %s", number)
                return number
            logger.critical(
                """Unable to retrieve a valid course ID from the provided course URL.
                Please check the course URL or try with --id."""
            )
            sys.exit(1)
        else:
            logger.critical(
                """Unable to retrieve a valid course ID from the provided course URL.
                Please check the course URL or try with --id"""
            )
            sys.exit(1)

    def fetch_course(self, course_id):
        try:
            response = self.request(COURSE_URL.format(portal=self.portal, course_id=course_id)).json()

            if response.get("detail") == "Not found.":
                logger.critical(
                    """The course could not be found with the provided ID or URL.
                    Please verify the course ID/URL and ensure that it is publicly accessible or
                    you have the necessary permissions."""
                )
                sys.exit(1)

            return response
        except requests.exceptions.RequestException as e:
            logger.critical("Unable to retrieve the course details: %s", e)
            sys.exit(1)

    def fetch_course_curriculum(self, course_id):
        all_results = []
        url = CURRICULUM_URL.format(portal=self.portal, course_id=course_id)
        total_count = 0

        logger.info("Fetching course curriculum. This may take a while")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3}%"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                description="Fetching Course Curriculum", total=total_count
            )

            while url:
                response = self.request(url).json()

                if (
                    response.get("detail")
                    == "You do not have permission to perform this action."
                    or response.get("detail")
                    == "You do not have permission to perform this action."
                ):
                    progress.stop()
                    logger.error(
                        """The course was found, but the curriculum (lectures and materials)
                        could not be retrieved. This could be due to API issues, restrictions on
                        the course, or a malformed course structure."""
                    )
                    sys.exit(1)

                if total_count == 0:
                    total_count = response.get("count", 0)
                    progress.update(task, total=total_count)

                results = response.get("results", [])
                all_results.extend(results)
                progress.update(task, completed=len(all_results))

                url = response.get("next")

            progress.update(
                task_id=task, description="Fetched Course Curriculum", total=total_count
            )
        return self.organize_curriculum(all_results)

    def organize_curriculum(self, results):
        curriculum = []
        current_chapter = None

        total_lectures = 0

        for item in results:
            if item["_class"] == "chapter":
                current_chapter = {
                    "id": item["id"],
                    "title": item["title"],
                    "is_published": item["is_published"],
                    "children": [],
                }
                curriculum.append(current_chapter)
            elif item["_class"] == "lecture":
                if current_chapter is not None:
                    current_chapter["children"].append(item)
                    if item["_class"] == "lecture":
                        total_lectures += 1
                else:
                    logger.warning("Found lecture without a parent chapter.")

        num_chapters = len(curriculum)

        logger.info("Discovered Chapter(s): %s", num_chapters)
        logger.info("Discovered Lectures(s): %s", total_lectures)

        return curriculum

    def build_curriculum_tree(self, data, tree, index=1):
        for i, item in enumerate(data, start=index):
            if "title" in item:
                title = f"{i:02d}. {item['title']}"
                if "_class" in item and item["_class"] == "lecture":
                    time_estimation = item.get("asset", {}).get("time_estimation")
                    if time_estimation:
                        time_str = format_time(time_estimation)
                        title += f" ({time_str})"
                    node_text = Text(title, style="cyan")
                else:
                    node_text = Text(title, style="magenta")

                node = tree.add(node_text)

                if "children" in item:
                    self.build_curriculum_tree(item["children"], node, index=1)

    def fetch_lecture_info(self, course_id, lecture_id):
        try:
            return self.request(
                LECTURE_URL.format(portal=self.portal, course_id=course_id, lecture_id=lecture_id)
            ).json()
        except requests.exceptions.RequestException as e:
            logger.critical("Failed to fetch lecture info: %s", e)
            sys.exit(1)

    def create_directory(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        except OSError as e:
            logger.error('Failed to create directory "%s": %s', path, e)
            sys.exit(1)

    def download_lecture(
        self,
        course_id,
        lecture,
        lect_info,
        temp_folder_path,
        lindex,
        folder_path,
        task_id,
        progress,
    ):
        lecture_title = sanitize_filename(lecture['title'])
        if not self.skip_captions and len(lect_info["asset"]["captions"]) > 0:
            download_captions(
                lect_info["asset"]["captions"],
                folder_path,
                f"{lindex}. {lecture_title}",
                self.captions,
                self.convert_to_srt,
            )

        if not self.skip_assets and len(lecture["supplementary_assets"]) > 0:
            download_supplementary_assets(
                self,
                lecture["supplementary_assets"],
                folder_path,
                course_id,
                lect_info["id"],
            )

        if not self.skip_lectures and lect_info["asset"]["asset_type"] == "Video":
            mpd_url = next(
                (
                    item["src"]
                    for item in lect_info["asset"]["media_sources"]
                    if item["type"] == "application/dash+xml"
                ),
                None,
            )
            mp4_url = next(
                (
                    item["src"]
                    for item in lect_info["asset"]["media_sources"]
                    if item["type"] == "video/mp4"
                ),
                None,
            )
            m3u8_url = next(
                (
                    item["src"]
                    for item in lect_info["asset"]["media_sources"]
                    if item["type"] == "application/x-mpegURL"
                ),
                None,
            )

            if mpd_url is None:
                if m3u8_url is None:
                    if mp4_url is None:
                        logger.error(
                            """This lecture appears to be served in different format. We currently
                            do not support downloading this format. Please create an issue on GitHub
                            if you need this feature."""
                        )
                    else:
                        download_mp4(
                            mp4_url,
                            temp_folder_path,
                            f"{lindex}. {lecture_title}",
                            task_id,
                            progress,
                        )
                else:
                    download_and_merge_m3u8(
                        m3u8_url,
                        temp_folder_path,
                        f"{lindex}. {lecture_title}",
                        task_id,
                        progress,
                    )
            else:
                if self.key is None:
                    logger.warning(
                        """The video appears to be DRM-protected, and it may not play without
                        a valid Widevine decryption key."""
                    )
                download_and_merge_mpd(
                    mpd_url,
                    temp_folder_path,
                    f"{lindex}. {lecture_title}",
                    lecture["asset"]["time_estimation"],
                    self.key,
                    task_id,
                    progress,
                )
        elif not self.skip_articles and lect_info["asset"]["asset_type"] == "Article":
            download_article(
                self,
                lect_info["asset"],
                temp_folder_path,
                f"{lindex}. {lecture_title}",
                task_id,
                progress,
            )

        try:
            progress.remove_task(task_id)
        except KeyError:
            pass

    def download_course(self, curriculum, settings: DownloadSettings):

        max_concurrent_lectures = settings.max_concurrent_lectures
        start_chapter = settings.start_chapter
        end_chapter = settings.end_chapter
        start_lecture = settings.start_lecture
        end_lecture = settings.end_lecture
        COURSE_DIR = settings.COURSE_DIR
        course_id = settings.course_id

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ElapsedTimeColumn(),
        )

        tasks = {}
        futures = []

        with ThreadPoolExecutor(max_workers=max_concurrent_lectures) as executor, Live(
            progress, refresh_per_second=10
        ):
            task_generator = (
                (
                    f"{mindex:02}" if mindex < 10 else f"{mindex}",
                    chapter,
                    f"{lindex:02}" if lindex < 10 else f"{lindex}",
                    lecture,
                )
                for mindex, chapter in enumerate(curriculum, start=1)
                if is_valid_chapter(mindex, start_chapter, end_chapter)
                for lindex, lecture in enumerate(chapter["children"], start=1)
                if is_valid_lecture(
                    mindex,
                    lindex,
                    start_chapter,
                    start_lecture,
                    end_chapter,
                    end_lecture,
                )
            )

            for _ in range(max_concurrent_lectures):
                try:
                    mindex, chapter, lindex, lecture = next(task_generator)
                    folder_path = os.path.join(
                        COURSE_DIR,
                        f"{mindex}. {remove_emojis_and_binary(sanitize_filename(chapter['title']))}",
                    )
                    temp_folder_path = os.path.join(folder_path, str(lecture["id"]))
                    self.create_directory(temp_folder_path)
                    lect_info = self.fetch_lecture_info(course_id, lecture["id"])

                    task_id = progress.add_task(
                        f"Downloading Lecture: {lecture['title']} ({lindex}/{len(chapter['children'])})",
                        total=100,
                    )
                    tasks[task_id] = (
                        lecture,
                        lect_info,
                        temp_folder_path,
                        lindex,
                        folder_path,
                    )

                    future = executor.submit(
                        self.download_lecture,
                        course_id,
                        lecture,
                        lect_info,
                        temp_folder_path,
                        lindex,
                        folder_path,
                        task_id,
                        progress,
                    )

                    futures.append((task_id, future))
                except StopIteration:
                    break

            while futures:
                for future in as_completed(f[1] for f in futures):
                    task_id = next(task_id for task_id, f in futures if f == future)
                    future.result()
                    try:
                        progress.remove_task(task_id)
                    except KeyError:
                        pass
                    futures = [f for f in futures if f[1] != future]

                    try:
                        mindex, chapter, lindex, lecture = next(task_generator)
                        folder_path = os.path.join(
                            COURSE_DIR,
                            f"{mindex}. {sanitize_filename(chapter['title'])}",
                        )
                        temp_folder_path = os.path.join(folder_path, str(lecture["id"]))
                        self.create_directory(temp_folder_path)
                        lect_info = self.fetch_lecture_info(course_id, lecture["id"])

                        task_id = progress.add_task(
                            f"Downloading Lecture: {lecture['title']} ({lindex}/{len(chapter['children'])})",
                            total=100,
                        )
                        tasks[task_id] = (
                            lecture,
                            lect_info,
                            temp_folder_path,
                            lindex,
                            folder_path,
                        )

                        future = executor.submit(
                            self.download_lecture,
                            course_id,
                            lecture,
                            lect_info,
                            temp_folder_path,
                            lindex,
                            folder_path,
                            task_id,
                            progress,
                        )

                        futures.append((task_id, future))
                    except StopIteration:
                        break
