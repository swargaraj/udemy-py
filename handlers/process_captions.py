import os

import requests
import webvtt


def download_captions(
    captions, download_folder_path, title_of_output_mp4, captions_list, convert_to_srt
):
    filtered_captions = [
        caption for caption in captions if caption["locale_id"] in captions_list
    ]

    for caption in filtered_captions:
        response = requests.get(caption["url"], timeout=10)
        response.raise_for_status()
        if caption["file_name"].endswith(".vtt"):
            caption_name = f"{title_of_output_mp4} - {caption['video_label']}.vtt"
            vtt_path = os.path.join(download_folder_path, caption_name)
            with open(vtt_path, "wb") as file:
                file.write(response.content)

            if convert_to_srt:
                srt_name = caption_name.replace(".vtt", ".srt")
                srt_path = os.path.join(download_folder_path, srt_name)
                srt_content = webvtt.read(vtt_path)
                srt_content.save_as_srt(srt_path)
                os.remove(vtt_path)

        else:
            print(
                """Only VTT captions are supported. Please create a github issue if
                you'd like to add support for other formats."""
            )
