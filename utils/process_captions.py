import os
import shutil
import requests
from urllib.parse import urlparse

def download_captions(captions, download_folder_path, title_of_output_mp4, captions_list, logger):
    logger.info("Downloading captions for " + title_of_output_mp4)

    filtered_captions = [caption for caption in captions if caption["locale_id"] in captions_list]

    for caption in filtered_captions:
        response = requests.get(caption['url'])
        response.raise_for_status()
        if caption['file_name'].endswith('.vtt'):
            caption_name = f"{title_of_output_mp4} - {caption['video_label']}.vtt"
            with open(os.path.join(download_folder_path, caption_name), 'wb') as file:
                file.write(response.content)
        else:
            logger.error("Only VTT captions are supported. Skipping caption: " + caption['file_name'])