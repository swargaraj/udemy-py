import os
import shutil

import requests

from lib.helpers import remove_emojis_and_binary


def download_mp4(
    mp4_file_url, download_folder_path, title_of_output_mp4, task_id, progress
):
    progress.update(
        task_id,
        description=f"Downloading Video {remove_emojis_and_binary(title_of_output_mp4)}",
        completed=0,
    )
    output_path = os.path.dirname(download_folder_path)

    try:
        response = requests.get(mp4_file_url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        downloaded_size = 0

        output_file = os.path.join(output_path, title_of_output_mp4 + ".mp4")
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    percentage = (downloaded_size / total_size) * 100
                    progress.update(task_id, completed=percentage)

        progress.update(task_id, completed=100)
        progress.console.log(
            f"[green]Downloaded {remove_emojis_and_binary(title_of_output_mp4)}[/green] ✓"
        )
        progress.remove_task(task_id)
        shutil.rmtree(download_folder_path)
    except Exception as e:
        print(e)
        progress.console.log(
            f"[red]Error Downloading {remove_emojis_and_binary(title_of_output_mp4)}[/red] ✕"
        )
