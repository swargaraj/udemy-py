import os

from lib.constants import FILE_ASSET_URL, LINK_ASSET_URL


def download_supplementary_assets(
    udemy, assets, download_folder_path, course_id, lecture_id
):
    for asset in assets:
        match asset["asset_type"]:
            case "File":
                process_files(udemy, asset, course_id, lecture_id, download_folder_path)
            case "ExternalLink":
                process_external_links(
                    udemy, asset, course_id, lecture_id, download_folder_path
                )
            case _:
                pass
                # Unsupported asset type. Please create a github issue if you'd like to add support for other types # noqa


def process_files(udemy, asset, course_id, lecture_id, download_folder_path):

    assets_folder = os.path.join(download_folder_path, "assets")
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)

    asset_file_path = os.path.join(assets_folder, asset["filename"])

    file_response = udemy.request(
        udemy.request(
            FILE_ASSET_URL.format(
                portal=udemy.portal, course_id=course_id, lecture_id=lecture_id, asset_id=asset["id"]
            )
        ).json()["download_urls"]["File"][0]["file"]
    )

    file_response.raise_for_status()

    with open(asset_file_path, "wb") as file:
        for chunk in file_response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)


def process_external_links(udemy, asset, course_id, lecture_id, download_folder_path):

    external_links_folder = os.path.join(download_folder_path, "external-links")
    if not os.path.exists(external_links_folder):
        os.makedirs(external_links_folder)

    asset_filename = f"{asset['filename']}.url"
    asset_file_path = os.path.join(external_links_folder, asset_filename)

    response = udemy.request(
        LINK_ASSET_URL.format(
            portal=udemy.portal, course_id=course_id, lecture_id=lecture_id, asset_id=asset["id"]
        )
    ).json()

    asset_url = response["external_url"]

    with open(asset_file_path, "w", encoding="utf-8") as file:
        file.write(f"[InternetShortcut]\nURL={asset_url}\n")
