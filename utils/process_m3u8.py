import m3u8
import os
import shutil
import requests
from urllib.parse import urlparse

def download_and_merge_m3u8(m3u8_file_url, download_folder_path, title_of_output_mp4, logger):
    response = requests.get(m3u8_file_url)
    response.raise_for_status()
    
    m3u8_content = response.text
    m3u8_obj = m3u8.loads(m3u8_content)
    playlists = m3u8_obj.playlists
    
    highest_quality_playlist = None
    max_resolution = (0, 0)

    for pl in playlists:
        resolution = pl.stream_info.resolution
        codecs = pl.stream_info.codecs

        if resolution and (resolution[0] * resolution[1] > max_resolution[0] * max_resolution[1]):
            highest_quality_playlist = pl
            max_resolution = resolution

    if not highest_quality_playlist:
        logger.error("No valid playlists found in the M3U8 file.")
        return
    
    highest_quality_url = highest_quality_playlist.uri
    logger.info(f"Selected highest quality stream: {max_resolution}")

    highest_quality_response = requests.get(highest_quality_url)
    m3u8_file_path = os.path.join(download_folder_path, "index.m3u8")

    with open(m3u8_file_path, 'wb') as file:
        file.write(highest_quality_response.content) 

    merge_segments_into_mp4(m3u8_file_path, download_folder_path, title_of_output_mp4, logger)

def merge_segments_into_mp4(m3u8_file_path, download_folder_path, output_file_name, logger):
    output_path = os.path.join(os.path.dirname(download_folder_path))

    nm3u8dl_command = f"n_m3u8dl-re \"{m3u8_file_path}\" --save-dir \"{output_path}\" --save-name \"{output_file_name}\" --auto-select --concurrent-download --del-after-done --no-log --tmp-dir \"{download_folder_path}\" --log-level ERROR"
    os.system(nm3u8dl_command)

    logger.info(f"{output_file_name} downloaded successfully")
    shutil.rmtree(download_folder_path)