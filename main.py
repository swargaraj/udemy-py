import json
import os
import sys
import argparse
import subprocess
from pathvalidate import sanitize_filename

import re
from tqdm import tqdm
import http.cookiejar as cookielib

import requests

from constants import *
from utils.process_m3u8 import download_and_merge_m3u8
from utils.process_mpd import download_and_merge_mpd

class Udemy:
    def __init__(self):
        global cookie_jar
        try:
            cookie_jar = cookielib.MozillaCookieJar(cookie_path)
            cookie_jar.load()
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
    
    def request(self, url):
        try:
            response = requests.get(url, cookies=cookie_jar)
            return response
        except Exception as e:
            logger.critical(f"Failed to request \"{url}\": {e}")

    def extract_course_id(self, course_url):
        response = self.request(course_url)
        content_str = response.content.decode('utf-8')

        meta_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', content_str)

        if meta_match:
            url = meta_match.group(1)
            number_match = re.search(r'/(\d+)_', url)
            if number_match:
                number = number_match.group(1)
                return number
            else:
                logger.error("Failed to extract course ID.")
                sys.exit(1)
        else:
            logger.error("Failed to extract course ID.")
            sys.exit(1)
        
    def fetch_course(self, course_id):
        response = self.request(COURSE_URL.format(course_id=course_id)).json()
        
        if response.get('detail') == 'Not found.':
            logging.error("Course not found.")
            sys.exit(1)
        
        return response
    
    def fetch_course_curriculum(self, course_id):
        all_results = []
        url = CURRICULUM_URL.format(course_id=course_id)
        total_count = 0

        logger.info("Fetching course curriculum. This may take a while")

        pbar = None

        while url:
            response = self.request(url).json()

            if response.get('detail') == 'Not found.':
                logger.error("Course curriculum not found.")
                sys.exit(1)

            if total_count == 0:
                total_count = response.get('count', 0)
                pbar = tqdm(total=total_count, unit='item', desc='Fetching Course Curriculum')

            all_results.extend(response.get('results', []))

            url = response.get('next')

            pbar.update(len(response.get('results', [])))

        if pbar:
            pbar.close()

        return self.organize_curriculum(all_results)
    
    def organize_curriculum(self, results):
        curriculum = []
        current_chapter = None

        total_lectures = 0
        total_practices = 0

        for item in results:
            if item['_class'] == 'chapter':
                current_chapter = {
                    'id': item['id'],
                    'title': item['title'],
                    'description': item['description'],
                    'is_published': item['is_published'],
                    'children': []
                }
                curriculum.append(current_chapter)
            elif item['_class'] in ['lecture', 'practice']:
                if current_chapter is not None:
                    current_chapter['children'].append(item)
                    if item['_class'] == 'lecture':
                        total_lectures += 1
                    elif item['_class'] == 'practice':
                        total_practices += 1
                else:
                    logger.warning("Found lecture or practice without a parent chapter.")

        num_chapters = len(curriculum)

        logger.info(f"Found {num_chapters} Modules, {total_lectures} Lectures & {total_practices} Practice Assets")

        return curriculum
    
    def fetch_lecture_info(self, course_id, lecture_id):
        return self.request(LECTURE_URL.format(course_id=course_id, lecture_id=lecture_id)).json()
    
    def create_directory(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            logger.warning(f"Directory {path} already exists")
            pass

    def download_course(self, course_id, curriculum):
        mindex = 1
        for chapter in curriculum:
            logger.info(f"Dowloading Chapter: {chapter['title']} ({mindex}/{len(curriculum)})")
            folder_path = os.path.join(COURSE_DIR, f"{mindex}. {sanitize_filename(chapter['title'])}")
            lindex = 1
            for lecture in chapter['children']:
                temp_folder_path = os.path.join(folder_path, str(lecture['id']))
                self.create_directory(temp_folder_path)
                if lecture['_class'] == 'lecture':
                    lect_info = self.fetch_lecture_info(course_id, lecture['id'])
                    logger.info(f"Dowloading Lecture: {lecture['title']} ({lindex}/{len(chapter['children'])})")
                    
                    if lecture['is_free']:
                        m3u8_url = next((item['src'] for item in lect_info['asset']['media_sources'] if item['type'] == "application/x-mpegURL"), None)
                        if m3u8_url is None:
                            logger.error(f"Could not find m3u8 url for {lecture['title']}")
                            continue
                        else:
                            download_and_merge_m3u8(m3u8_url, temp_folder_path, f"{lindex}. {sanitize_filename(lecture['title'])}", logger)
                    else:
                        if key is None:
                            logger.warning("No decryption key is provided. If the lecture is DRM protected, it will fail to merge.")
                        mpd_url = next((item['src'] for item in lect_info['asset']['media_sources'] if item['type'] == "application/dash+xml"), None)
                        if mpd_url is None:
                            logger.error(f"Could not find mpd url for {lecture['title']}")
                            continue
                        else:
                            download_and_merge_mpd(mpd_url, temp_folder_path, f"{lindex}. {sanitize_filename(lecture['title'])}", key, logger)
                    
                if lecture['_class'] == 'practice':
                    # TODO
                    pass
                lindex += 1
            mindex += 1

def check_prerequisites():
    if not os.path.isfile(cookie_path):
        logger.error(f"{cookie_path} not found.")
        return False
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("Error: ffmpeg is not installed or not found in the system PATH.")
        return False
    
    try:
        subprocess.run(["n_m3u8dl-re", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("Error: n_m3u8dl-re is not installed or not found in the system PATH.")
        return False

    return True

def main():

    global course_url, key, cookie_path, COURSE_DIR

    parser = argparse.ArgumentParser(description="Udemy Course Downloader")
    parser.add_argument("--url", "-u", type=str, required=True, help="The URL of the Udemy course to download")
    parser.add_argument("--key", "-k", type=str, help="Key to decrypt the DRM-protected videos")
    parser.add_argument("--cookies", "-c", type=str, default="cookies.txt", help="Path to cookies.txt file")
    parser.add_argument("--load", "-l", help="Load course curriculum from file", action=LoadAction, const=True, nargs='?')
    parser.add_argument("--save", "-s", help="Save course curriculum to a file", action=LoadAction, const=True, nargs='?')
    
    args = parser.parse_args()

    course_url = args.url
    key = args.key
    
    if key is not None and not ":" in key:
        logger.error("Invalid decryption key provided. Key format should be key:value")
        return
    
    cookie_path = args.cookies

    if not check_prerequisites():
        return
    
    udemy = Udemy()

    course_id = udemy.extract_course_id(course_url)
    course_info = udemy.fetch_course(course_id)
    COURSE_DIR = os.path.join(DOWNLOAD_DIR, sanitize_filename(course_info['title']))

    logger.info(f"Course Title: {course_info['title']}")

    udemy.create_directory(os.path.join(COURSE_DIR))

    if args.load:
        if args.load is True and os.path.isfile(os.path.join(HOME_DIR, "course.json")):
            try:
                course_curriculum = json.load(open(os.path.join(HOME_DIR, "course.json"), "r"))
                logger.info(f"Course curriculum loaded from course.json")
            except json.JSONDecodeError:
                logger.error("Course curriculum file is not valid JSON.")
                sys.exit(1)
        elif args.load:
            if os.path.isfile(args.load):
                try:
                    course_curriculum = json.load(open(args.load, "r"))
                    logger.info(f"Course curriculum loaded from {args.load}")
                except json.JSONDecodeError:
                    logger.error("Course curriculum file is not valid JSON.")
                    sys.exit(1)
            else:
                logger.error("Course curriculum file not found.")
                sys.exit(1)
        else:
            logger.error("Please provide the path to the course curriculum file.")
            sys.exit(1)
    else:
        try:
            course_curriculum = udemy.fetch_course_curriculum(course_id)
        except Exception as e:
            logger.critical(f"Failed to fetch course curriculum: {e}")
            sys.exit(1)

    if args.save:
        if args.save is True:
            if (os.path.isfile(os.path.join(HOME_DIR, "course.json"))):
                logger.warning("Course curriculum file already exists. Overwriting")
            with open(os.path.join(HOME_DIR, "course.json"), "w") as f:
                json.dump(course_curriculum, f, indent=4)
                logger.info(f"Course curriculum saved to course.json")
        elif args.save:
            if (os.path.isfile(args.save)):
                logger.warning("Course curriculum file already exists. Overwriting")
            with open(args.save, "w") as f:
                json.dump(course_curriculum, f, indent=4)
                logger.info(f"Course curriculum saved to {args.save}")

    udemy.download_course(course_id, course_curriculum)

    logger.info("Download Complete.")

if __name__ == "__main__":
    main()