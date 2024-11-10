import os
import time

# flake8: noqa
COURSE_URL = "https://{portal}.udemy.com/api-2.0/courses/{course_id}/"
CURRICULUM_URL = "https://{portal}.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/?page_size=200&fields[lecture]=title,object_index,is_published,sort_order,created,asset,supplementary_assets,is_free&fields[quiz]=title,object_index,is_published,sort_order,type&fields[practice]=title,object_index,is_published,sort_order&fields[chapter]=title,object_index,is_published,sort_order&fields[asset]=title,filename,asset_type,status,time_estimation,is_external&caching_intent=True"
LECTURE_URL = "https://{portal}.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}?fields[lecture]=asset,description,download_url,is_free,last_watched_second&fields[asset]=asset_type,media_sources,captions"
QUIZ_URL = "https://{portal}.udemy.com/api-2.0/quizzes/{quiz_id}/assessments/?version=1&page_size=200&fields[assessment]=id,assessment_type,prompt,correct_response,section,question_plain,related_lectures"
LINK_ASSET_URL = "https://{portal}.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}/supplementary-assets/{asset_id}/?fields[asset]=external_url"
FILE_ASSET_URL = "https://{portal}.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{lecture_id}/supplementary-assets/{asset_id}/?fields[asset]=download_urls"
ARTICLE_URL = "https://{portal}.udemy.com/api-2.0/assets/{article_id}/?fields[asset]=@min,status,delayed_asset_message,processing_errors,body"

HOME_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(HOME_DIR, "courses")

LOG_DIR = os.path.join(HOME_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, f"{time.strftime('%Y-%m-%d')}.log")
