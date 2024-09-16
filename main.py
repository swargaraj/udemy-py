import json
import os
import sys
import requests
import argparse
import subprocess
from pathvalidate import sanitize_filename
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.live import Live

import re
import http.cookiejar as cookielib
from concurrent.futures import ThreadPoolExecutor, as_completed

from constants import *
from utils.process_m3u8 import download_and_merge_m3u8
from utils.process_mpd import download_and_merge_mpd
from utils.process_captions import download_captions
from utils.process_assets import download_supplementary_assets
from utils.process_articles import download_article

console = Console()

class Udemy:
    def __init__(self):
        global cookie_jar
        try:
            cookie_jar = cookielib.MozillaCookieJar(cookie_path)
            cookie_jar.load()
        except Exception as e:
            logger.critical(f"The provided cookie file could not be read or is incorrectly formatted. Please ensure the file is in the correct format and contains valid authentication cookies.")
            sys.exit(1)
    
    def request(self, url):
        try:
            response = requests.get(url, cookies=cookie_jar, stream=True)
            return response
        except Exception as e:
            logger.critical(f"There was a problem reaching the Udemy server. This could be due to network issues, an invalid URL, or Udemy being temporarily unavailable.")

    def extract_course_id(self, course_url):

        with Loader(f"Fetching course ID"):            
            response = self.request(course_url)
            content_str = response.content.decode('utf-8')

        meta_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', content_str)

        if meta_match:
            url = meta_match.group(1)
            number_match = re.search(r'/(\d+)_', url)
            if number_match:
                number = number_match.group(1)
                logger.info(f"Course ID Extracted: {number}")
                return number
            else:
                logger.critical("Unable to retrieve a valid course ID from the provided course URL. Please check the course URL or try with --id.")
                sys.exit(1)
        else:
            logger.critical("Unable to retrieve a valid course ID from the provided course URL. Please check the course URL or try with --id")
            sys.exit(1)
        
    def fetch_course(self, course_id):
        try:
            response = self.request(COURSE_URL.format(course_id=course_id)).json()
    
            if response.get('detail') == 'Not found.':
                logger.critical("The course could not be found with the provided ID or URL. Please verify the course ID/URL and ensure that it is publicly accessible or you have the necessary permissions.")
                sys.exit(1)
            
            return response
        except Exception as e:
            logger.critical(f"Unable to retrieve the course details: {e}")
            sys.exit(1)
    
    def fetch_course_curriculum(self, course_id):
        all_results = []
        url = CURRICULUM_URL.format(course_id=course_id)
        total_count = 0

        logger.info("Fetching course curriculum. This may take a while")

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3}%"),
        ) as progress:
            task = progress.add_task(description="Fetching Course Curriculum", total=total_count)

            while url:
                response = self.request(url).json()

                if response.get('detail') == 'Not found.':
                    logger.critical("The course was found, but the curriculum (lectures and materials) could not be retrieved. This could be due to API issues, restrictions on the course, or a malformed course structure.")
                    sys.exit(1)

                if total_count == 0:
                    total_count = response.get('count', 0)
                    progress.update(task, total=total_count)

                results = response.get('results', [])
                all_results.extend(results)
                progress.update(task, completed=len(all_results))

                url = response.get('next')

            progress.update(task_id = task, description="Fetched Course Curriculum", total=total_count)
        return self.organize_curriculum(all_results)
    
    def organize_curriculum(self, results):
        curriculum = []
        current_chapter = None

        total_lectures = 0

        for item in results:
            if item['_class'] == 'chapter':
                current_chapter = {
                    'id': item['id'],
                    'title': item['title'],
                    'is_published': item['is_published'],
                    'children': []
                }
                curriculum.append(current_chapter)
            elif item['_class'] in ['lecture', 'practice']:
                if current_chapter is not None:
                    current_chapter['children'].append(item)
                    if item['_class'] == 'lecture':
                        total_lectures += 1
                else:
                    logger.warning("Found lecture without a parent chapter.")

        num_chapters = len(curriculum)

        logger.info(f"Discovered Chapter(s): {num_chapters}")
        logger.info(f"Discovered Lectures(s): {total_lectures}")

        return curriculum
    
    def fetch_lecture_info(self, course_id, lecture_id):
        try:
            return self.request(LECTURE_URL.format(course_id=course_id, lecture_id=lecture_id)).json()
        except Exception as e:
            logger.critical(f"Failed to fetch lecture info: {e}")
            sys.exit(1)
    
    def create_directory(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        except Exception as e:
            logger.error(f"Failed to create directory \"{path}\": {e}")
            sys.exit(1)

    def download_lecture(self, course_id, lecture, lect_info, temp_folder_path, lindex, folder_path, task_id, progress):
        if len(lect_info["asset"]["captions"]) > 0:
            download_captions(lect_info["asset"]["captions"], folder_path, f"{lindex}. {sanitize_filename(lecture['title'])}", captions)

        if len(lecture["supplementary_assets"]) > 0:
            download_supplementary_assets(self, lecture["supplementary_assets"], folder_path, course_id, lect_info["id"])

        if lect_info['asset']['asset_type'] == "Video":
            mpd_url = next((item['src'] for item in lect_info['asset']['media_sources'] if item['type'] == "application/dash+xml"), None)
            # mp4_url = next((item['src'] for item in lect_info['asset']['media_sources'] if item['type'] == "video/mp4"), None)
            m3u8_url = next((item['src'] for item in lect_info['asset']['media_sources'] if item['type'] == "application/x-mpegURL"), None)
            
            if mpd_url is None:
                if m3u8_url is None:
                    pass
                    logger.error(f"This lecture appears to be served in different format. We currently do not support downloading this format. Please create an issue on GitHub if you need this feature.")
                else:
                    download_and_merge_m3u8(m3u8_url, temp_folder_path, f"{lindex}. {sanitize_filename(lecture['title'])}", task_id, progress)
            else:
                if key is None:
                    logger.warning("The video appears to be DRM-protected, and it may not play without a valid Widevine decryption key.")
                download_and_merge_mpd(mpd_url, temp_folder_path, f"{lindex}. {sanitize_filename(lecture['title'])}", lecture['asset']['time_estimation'], key, task_id, progress)
        elif lect_info['asset']['asset_type'] == "Article":
            download_article(self, lect_info['asset'], temp_folder_path, f"{lindex}. {sanitize_filename(lecture['title'])}", task_id, progress)
        else:
            pass
            logger.warning(f"Unsupported asset type: {lect_info['asset']['asset_type']}. Skipping.")

    def download_course(self, course_id, curriculum):
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ElapsedTimeColumn(),
        )
        
        tasks = {}
        futures = []

        with ThreadPoolExecutor(max_workers=max_concurrent_lectures) as executor, Live(progress, refresh_per_second=10):
            task_generator = (
                (f"{mindex:02}" if mindex < 10 else f"{mindex}", 
                chapter, 
                f"{lindex:02}" if lindex < 10 else f"{lindex}", 
                lecture)
                for mindex, chapter in enumerate(curriculum, start=1)
                for lindex, lecture in enumerate(chapter['children'], start=1)
            )

            for _ in range(max_concurrent_lectures):
                try:
                    mindex, chapter, lindex, lecture = next(task_generator)
                    folder_path = os.path.join(COURSE_DIR, f"{mindex}. {sanitize_filename(chapter['title'])}")
                    temp_folder_path = os.path.join(folder_path, str(lecture['id']))
                    self.create_directory(temp_folder_path)
                    lect_info = self.fetch_lecture_info(course_id, lecture['id'])
                    
                    task_id = progress.add_task(
                        f"Downloading Lecture: {lecture['title']} ({lindex}/{len(chapter['children'])})", 
                        total=100
                    )
                    tasks[task_id] = (lecture, lect_info, temp_folder_path, lindex, folder_path)
                    
                    future = executor.submit(
                        self.download_lecture, course_id, lecture, lect_info, temp_folder_path, lindex, folder_path, task_id, progress
                    )

                    futures.append((task_id, future))
                except StopIteration:
                    break

            while futures:
                for future in as_completed(f[1] for f in futures):
                    task_id = next(task_id for task_id, f in futures if f == future)
                    future.result()
                    progress.remove_task(task_id)
                    futures = [f for f in futures if f[1] != future]

                    try:
                        mindex, chapter, lindex, lecture = next(task_generator)
                        folder_path = os.path.join(COURSE_DIR, f"{mindex}. {sanitize_filename(chapter['title'])}")
                        temp_folder_path = os.path.join(folder_path, str(lecture['id']))
                        self.create_directory(temp_folder_path)
                        lect_info = self.fetch_lecture_info(course_id, lecture['id'])

                        task_id = progress.add_task(
                            f"Downloading Lecture: {lecture['title']} ({lindex}/{len(chapter['children'])})",
                            total=100
                        )
                        tasks[task_id] = (lecture, lect_info, temp_folder_path, lindex, folder_path)

                        future = executor.submit(
                            self.download_lecture, course_id, lecture, lect_info, temp_folder_path, lindex, folder_path, task_id, progress
                        )

                        futures.append((task_id, future))
                    except StopIteration:
                        break

def check_prerequisites():
    if not cookie_path:
        if not os.path.isfile(os.path.join(HOME_DIR, "cookies.txt")):
            logger.error(f"Please provide a valid cookie file using the '--cookie' option.")
            return False
    else:
        if not os.path.isfile(cookie_path):
            logger.error(f"The provided cookie file path does not exist.")
            return False

    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("ffmpeg is not installed or not found in the system PATH.")
        return False
    
    try:
        subprocess.run(["n_m3u8dl-re", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("Make sure mp4decrypt & n_m3u8dl-re is not installed or not found in the system PATH.")
        return False
    
    return True

def main():

    try:
        global course_url, key, cookie_path, COURSE_DIR, captions, max_concurrent_lectures

        parser = argparse.ArgumentParser(description="Udemy Course Downloader")
        parser.add_argument("--id", "-i", type=int, required=False, help="The ID of the Udemy course to download")
        parser.add_argument("--url", "-u", type=str, required=False, help="The URL of the Udemy course to download")
        parser.add_argument("--key", "-k", type=str, help="Key to decrypt the DRM-protected videos")
        parser.add_argument("--cookies", "-c", type=str, default="cookies.txt", help="Path to cookies.txt file")
        parser.add_argument("--load", "-l", help="Load course curriculum from file", action=LoadAction, const=True, nargs='?')
        parser.add_argument("--save", "-s", help="Save course curriculum to a file", action=LoadAction, const=True, nargs='?')
        parser.add_argument("--concurrent", "-cn", type=int, default=4, help="Maximum number of concurrent downloads")
        parser.add_argument("--captions", type=str, help="Specify what captions to download. Separate multiple captions with commas")
        
        args = parser.parse_args()

        if len(sys.argv) == 1:
            print(parser.format_help())
            sys.exit(0)
        course_url = args.url

        key = args.key

        if args.concurrent > 25:
            logger.warning("The maximum number of concurrent downloads is 25. The provided number of concurrent downloads will be capped to 25.")
            max_concurrent_lectures = 25
        elif args.concurrent < 1:
            logger.warning("The minimum number of concurrent downloads is 1. The provided number of concurrent downloads will be capped to 1.")
            max_concurrent_lectures = 1
        else:
            max_concurrent_lectures = args.concurrent

        if not course_url and not args.id:
            logger.error("You must provide either the course ID with '--id' or the course URL with '--url' to proceed.")
            return
        elif course_url and args.id:
            logger.warning("Both course ID and URL provided. Prioritizing course ID over URL.")
        
        if key is not None and not ":" in key:
            logger.error("The provided Widevine key is either malformed or incorrect. Please check the key and try again.")
            return
        
        if args.cookies:
            cookie_path = args.cookies

        if not check_prerequisites():
            return
        
        udemy = Udemy()

        if args.id:
            course_id = args.id
        else:
            course_id = udemy.extract_course_id(course_url)

        if args.captions:
            try:
                captions = args.captions.split(",")
            except:
                logger.error("Invalid captions provided. Captions should be separated by commas.")
        else:
            captions = ["en_US"]
        
        course_info = udemy.fetch_course(course_id)
        COURSE_DIR = os.path.join(DOWNLOAD_DIR, sanitize_filename(course_info['title']))

        logger.info(f"Course Title: {course_info['title']}")

        udemy.create_directory(os.path.join(COURSE_DIR))

        if args.load:
            if args.load is True and os.path.isfile(os.path.join(HOME_DIR, "course.json")):
                try:
                    course_curriculum = json.load(open(os.path.join(HOME_DIR, "course.json"), "r"))
                    logger.info(f"The course curriculum is successfully loaded from course.json")
                except json.JSONDecodeError:
                    logger.error("The course curriculum file provided is either malformed or corrupted.")
                    sys.exit(1)
            elif args.load:
                if os.path.isfile(args.load):
                    try:
                        course_curriculum = json.load(open(args.load, "r"))
                        logger.info(f"The course curriculum is successfully loaded from {args.load}")
                    except json.JSONDecodeError:
                        logger.error("The course curriculum file provided is either malformed or corrupted.")
                        sys.exit(1)
                else:
                    logger.error("The course curriculum file could not be located. Please verify the file path and ensure that the file exists.")
                    sys.exit(1)
            else:
                logger.error("Please provide the path to the course curriculum file.")
                sys.exit(1)
        else:
            try:
                course_curriculum = udemy.fetch_course_curriculum(course_id)
            except Exception as e:
                logger.critical(f"Unable to retrieve the course curriculum. {e}")
                sys.exit(1)

        if args.save:
            if args.save is True:
                if (os.path.isfile(os.path.join(HOME_DIR, "course.json"))):
                    logger.warning("Course curriculum file already exists. Overwriting the existing file.")
                with open(os.path.join(HOME_DIR, "course.json"), "w") as f:
                    json.dump(course_curriculum, f, indent=4)
                    logger.info(f"The course curriculum has been successfully saved to course.json")
            elif args.save:
                if (os.path.isfile(args.save)):
                    logger.warning("Course curriculum file already exists. Overwriting the existing file.")
                with open(args.save, "w") as f:
                    json.dump(course_curriculum, f, indent=4)
                    logger.info(f"The course curriculum has been successfully saved to {args.save}")

        logger.info("The course download is starting. Please wait while the materials are being downloaded.")

        udemy.download_course(course_id, course_curriculum)

        logger.info("All course materials have been successfully downloaded.")    
        logger.info("Download Complete.")
    except KeyboardInterrupt:
        logger.warning("Process interrupted. Exiting")
        sys.exit(0)

if __name__ == "__main__":
    main()