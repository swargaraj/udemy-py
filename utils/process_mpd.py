import os
import shutil
import subprocess
import requests
from urllib.parse import urlparse

def download_and_merge_mpd(mpd_file_url, download_folder_path, title_of_output_mp4, key, logger, task_id, progress):
    mpd_filename = os.path.basename(urlparse(mpd_file_url).path)
    mpd_file_path = os.path.join(download_folder_path, mpd_filename)

    response = requests.get(mpd_file_url)
    response.raise_for_status()

    with open(mpd_file_path, 'wb') as file:
        file.write(response.content)

    process_mpd(mpd_file_path, download_folder_path, title_of_output_mp4, key, logger)

def process_mpd(mpd_file_path, download_folder_path, output_file_name, key, logger):
    nm3u8dl_command = (
        f"n_m3u8dl-re \"{mpd_file_path}\" --save-dir \"{download_folder_path}\" "
        f"--save-name \"{output_file_name}.mp4\" --auto-select --concurrent-download "
        f"--key {key} --del-after-done --no-log --tmp-dir \"{download_folder_path}\" "
        f"--log-level ERROR"
    )

    process_nm3u8dl = subprocess.Popen(
        nm3u8dl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout_nm3u8dl, stderr_nm3u8dl = process_nm3u8dl.communicate()

    if stderr_nm3u8dl or process_nm3u8dl.returncode != 0:
        logger.critical(f"Error Downloading Video and Audio files of {output_file_name}")
        return

    files = os.listdir(download_folder_path)
    mp4_files = [f for f in files if f.endswith('.mp4')]
    m4a_files = [f for f in files if f.endswith('.m4a')]

    if not mp4_files or not m4a_files:
        logger.critical("Video or audio files not found in the temporary folder.")
        return

    video_path = os.path.join(download_folder_path, mp4_files[0])
    audio_path = os.path.join(download_folder_path, m4a_files[0])
    output_path = os.path.join(os.path.dirname(download_folder_path), output_file_name)

    ffmpeg_command = (
        f"ffmpeg -i \"{video_path}\" -i \"{audio_path}\" -c:v copy -c:a aac "
        f"\"{output_path}.mp4\" -loglevel panic"
    )

    process_ffmpeg = subprocess.Popen(
        ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout_ffmpeg, stderr_ffmpeg = process_ffmpeg.communicate()

    if stderr_ffmpeg or process_ffmpeg.returncode != 0:
        logger.critical(f"Error Merging Video and Audio files of {output_file_name}")
        return

    shutil.rmtree(download_folder_path)