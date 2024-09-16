import os
import shutil
from urllib.parse import urlparse
from constants import ARTICLE_URL

def download_article(udemy, article, download_folder_path, title_of_output_article, task_id, progress):

    progress.update(task_id,  description=f"Downloading Article {title_of_output_article}", completed=0)

    article_filename = f"{title_of_output_article}.html"
    article_response = udemy.request(ARTICLE_URL.format(article_id=article['id'])).json()

    with open(os.path.join(os.path.dirname(download_folder_path), article_filename), 'w') as file:
        file.write(article_response['body'])

    progress.console.log(f"[green]Downloaded {title_of_output_article}[/green] ✓")
    progress.remove_task(task_id)

    shutil.rmtree(download_folder_path)