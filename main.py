import os
import sys
import argparse
import subprocess
from pathvalidate import sanitize_filename

import re
import json
from tqdm import tqdm
import http.cookiejar as cookielib

import requests

from constants import *

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
            response = requests.get(url, cookies=cookie_jar).json()
            return response
        except Exception as e:
            logger.critical(f"Failed to request \"{url}\": {e}")

    def extract_course_id(self, course_url):
        # TODO
        return 1452908
        
    def fetch_course(self, course_id):
        response = self.request(COURSE_URL.format(course_id=course_id))
        
        if response.get('detail') == 'Not found.':
            logging.error("Course not found.")
            sys.exit(1)
        
        return response
    
    def fetch_course_curriculum(self, course_id):
        all_results = []
        url = CURRICULUM_URL.format(course_id=course_id)
        total_count = 0

        logger.info("Fetching course curriculum. This may take a while\n")

        pbar = None

        while url:
            response = self.request(url)

            if response.get('detail') == 'Not found.':
                logger.error("Course curriculum not found.")
                sys.exit(1)

            if total_count == 0:
                total_count = response.get('count', 0)
                pbar = tqdm(total=total_count, unit='item', desc='Fetching Course Curriculum')

            all_results.extend(response.get('results', []))

            url = response.get('next')

            discovered_count = len(all_results)
            pbar.update(len(response.get('results', [])))

        if pbar:
            pbar.close()

        print("\n")
        logger.info(f"Discovered {total_count} Course Curriculum items.")
        return self.organize_curriculum(all_results)
    
    def organize_curriculum(self, results):
        curriculum = []
        current_chapter = None

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
                else:
                    logger.warning("Found lecture or practice without a parent chapter.")

        return curriculum
    
    def fetch_lecture_info(self, course_id, lecture_id):
        return self.request(LECTURE_URL.format(course_izd=course_id, lecture_id=lecture_id))    

def check_prerequisites():
    if not os.path.isfile(cookie_path):
        logger.error(f"{cookie_path} not found.")
        return False

    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("Error: ffmpeg is not installed or not found in the system PATH.")
        return False

    return True

def main():

    global course_url, key, cookie_path

    parser = argparse.ArgumentParser(description="Udemy Course Downloader")
    parser.add_argument("--url", "-u", type=str, required=True, help="The URL of the Udemy course to download")
    parser.add_argument("--key", "-k", type=str, required=True, help="Key to decrypt the DRM-protected videos")
    parser.add_argument("--cookies", "-c", type=str, default="cookies.txt", help="Path to cookies.txt file")
    
    args = parser.parse_args()

    course_url = args.url
    key = args.key
    cookie_path = args.cookies
    
    if not check_prerequisites():
        return
    
    udemy = Udemy()

    # course_id = udemy.extract_course_id(course_url)
    # course_info = udemy.fetch_course(course_id)

    # logger.info(f"Course Title: {course_info['title']}")

    # course_curriculum = udemy.fetch_course_curriculum(course_id)

    # print(udemy.fetch_lecture_info(1452908, 31531812))
    

if __name__ == "__main__":
    main()