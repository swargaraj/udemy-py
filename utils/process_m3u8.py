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
    highest_quality_m3u8_content = highest_quality_response.text
    highest_quality_m3u8_obj = m3u8.loads(highest_quality_m3u8_content)

    total_segments = len(highest_quality_m3u8_obj.segments)
    sindex = 1

    for segment in highest_quality_m3u8_obj.segments:
        segment_url = segment.uri
        segment_filename = os.path.join(download_folder_path, os.path.basename(urlparse(segment_url).path))
        logger.info(f"Downloading segment ({sindex}/{total_segments})")

        segment_response = requests.get(segment_url)
        with open(segment_filename, 'wb') as f:
            f.write(segment_response.content)

        sindex += 1

    merge_segments_into_mp4(download_folder_path, title_of_output_mp4, logger)

def merge_segments_into_mp4(download_folder_path, output_file_name, logger):
    output_path = os.path.join(os.path.dirname(download_folder_path), output_file_name)
    segments_file_path = os.path.join(download_folder_path, "segments.txt")

    with open(segments_file_path, 'w') as f:
        for segment_file in sorted(os.listdir(download_folder_path)):
            if segment_file.endswith(".ts"):
                f.write(f"file '{os.path.join(download_folder_path, segment_file)}'\n")

    ffmpeg_command = f"ffmpeg -f concat -safe 0 -i \"{segments_file_path}\" -c copy \"{output_path}.mp4"
    logger.info(f"Merging Segments")
    os.system(ffmpeg_command)
    logger.info(f"{output_file_name} downloaded successfully")
    shutil.rmtree(download_folder_path)