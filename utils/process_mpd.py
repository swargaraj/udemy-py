import os
import shutil
import requests
from urllib.parse import urlparse

def download_and_merge_mpd(mpd_file_url, download_folder_path, title_of_output_mp4, key, logger):
    mpd_filename = os.path.basename(urlparse(mpd_file_url).path)
    mpd_file_path = os.path.join(download_folder_path, mpd_filename)

    response = requests.get(mpd_file_url)
    response.raise_for_status()

    logger.info(f"MPD File Downloaded")

    with open(mpd_file_path, 'wb') as file:
        file.write(response.content)

    process_mpd(mpd_file_path, download_folder_path, title_of_output_mp4, key, logger)

def process_mpd(mpd_file_path, download_folder_path, output_file_name, key, logger):
    nm3u8dl_command = f"N_M3u8DL-RE \"{mpd_file_path}\" --save-dir \"{download_folder_path}\" --save-name \"{output_file_name}.mp4\" --auto-select --concurrent-download --key {key} --del-after-done --no-log"
    os.system(nm3u8dl_command)

    files = os.listdir(download_folder_path)

    mp4_files = [f for f in files if f.endswith('.mp4')]
    m4a_files = [f for f in files if f.endswith('.m4a')]
    
    if not mp4_files or not m4a_files:
        logger.critical("Video or audio files not found in the temporary folder.")

    video_path = os.path.join(download_folder_path, mp4_files[0])
    audio_path = os.path.join(download_folder_path, m4a_files[0])

    output_path = os.path.join(os.path.dirname(download_folder_path), output_file_name)

    ffmpeg_command = f"ffmpeg -i \"{video_path}\" -i \"{audio_path}\" -c:v copy -c:a aac \"{output_path}.mp4"
    os.system(ffmpeg_command)

    logger.info(f"{output_file_name} downloaded successfully")
    shutil.rmtree(download_folder_path)