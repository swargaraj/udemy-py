import os
import shutil
import requests
from urllib.parse import urlparse
from constants import LINK_ASSET_URL, FILE_ASSET_URL

def process_supplementary_assets(udemy, assets, download_folder_path, course_id, lecture_id, logger):
    for asset in assets:
        match asset['asset_type']:
            case 'File':
                process_files(udemy, asset, course_id, lecture_id, download_folder_path, logger)
            case 'Article':
                process_articles(udemy, asset, course_id, lecture_id, download_folder_path, logger)
            case 'ExternalLink':
                process_external_links(udemy, asset, course_id, lecture_id, download_folder_path, logger)
            case _:
                logger.error(f"Unsupported asset type. Please create a github issue if you'd like to add support for other types. Skipping asset: {asset['title']}")

def process_files(udemy, asset, course_id, lecture_id, download_folder_path, logger):

    assets_folder = os.path.join(download_folder_path, "assets")
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)
    
    asset_file_path = os.path.join(assets_folder, asset['filename'])

    if os.path.exists(asset_file_path):
        logger.warn(f"Skipping {asset['title']}. It already exists at {asset_file_path}")
        return

    file_response = udemy.request(udemy.request(FILE_ASSET_URL.format(course_id=course_id, lecture_id=lecture_id, asset_id=asset['id'])).json()['download_urls']['File'][0]['file'])

    file_response.raise_for_status()

    with open(asset_file_path, 'wb') as file:
        for chunk in file_response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    logger.info(f"Downloaded asset: {asset['filename']}")

def process_articles(udemy, asset, course_id, lecture_id, download_folder_path, logger):
    pass

def process_external_links(udemy, asset, course_id, lecture_id, download_folder_path, logger):

    external_links_folder = os.path.join(download_folder_path, "external-links")
    if not os.path.exists(external_links_folder):
        os.makedirs(external_links_folder)

    asset_filename = f"{asset['filename']}.url"
    asset_file_path = os.path.join(external_links_folder, asset_filename)

    if os.path.exists(asset_file_path):
        logger.warn(f"Skipping {asset['title']}. It already exists at {asset_file_path}")
        return

    response = udemy.request(LINK_ASSET_URL.format(course_id=course_id, lecture_id=lecture_id, asset_id=asset['id'])).json()

    asset_url = response['external_url']

    with open(asset_file_path, 'w') as file:
        file.write(f"[InternetShortcut]\nURL={asset_url}\n")

    logger.info(f"Downloaded external link: {asset_filename}")
