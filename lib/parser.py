import argparse

from lib.loader import LoadAction


def create_parser():
    parser = argparse.ArgumentParser(description="Udemy Course Downloader")

    parser.add_argument(
        "--id",
        "-i",
        type=int,
        required=False,
        help="The ID of the Udemy course to download",
    )

    parser.add_argument(
        "--url",
        "-u",
        type=str,
        required=False,
        help="The URL of the Udemy course to download",
    )

    parser.add_argument(
        "--portal",
        "-p",
        type=str,
        required=False,
        help="The portal of the Udemy account",
    )

    parser.add_argument(
        "--key", "-k", type=str, help="Key to decrypt the DRM-protected videos"
    )

    parser.add_argument(
        "--cookies",
        "-c",
        type=str,
        default="cookies.txt",
        help="Path to cookies.txt file",
    )

    parser.add_argument(
        "--load",
        "-l",
        help="Load course curriculum from file",
        action=LoadAction,
        const=True,
        nargs="?",
    )

    parser.add_argument(
        "--save",
        "-s",
        help="Save course curriculum to a file",
        action=LoadAction,
        const=True,
        nargs="?",
    )

    parser.add_argument(
        "--concurrent",
        "-cn",
        type=int,
        default=4,
        help="Maximum number of concurrent downloads",
    )

    parser.add_argument(
        "--start-chapter",
        type=int,
        help="Start the download from the specified chapter",
    )

    parser.add_argument(
        "--start-lecture",
        type=int,
        help="Start the download from the specified lecture",
    )

    parser.add_argument(
        "--end-chapter", type=int, help="End the download at the specified chapter"
    )

    parser.add_argument(
        "--end-lecture", type=int, help="End the download at the specified lecture"
    )

    parser.add_argument(
        "--captions",
        type=str,
        help="Specify what captions to download. Separate multiple captions with commas",
    )

    parser.add_argument(
        "--srt",
        help="Convert the captions to srt format",
        action=LoadAction,
        const=True,
        nargs="?",
    )

    parser.add_argument(
        "--tree",
        help="Create a tree view of the course curriculum",
        action=LoadAction,
        nargs="?",
    )

    parser.add_argument(
        "--skip-captions",
        type=bool,
        default=False,
        help="Skip downloading captions",
        action=LoadAction,
        nargs="?",
    )

    parser.add_argument(
        "--skip-assets",
        type=bool,
        default=False,
        help="Skip downloading assets",
        action=LoadAction,
        nargs="?",
    )

    parser.add_argument(
        "--skip-lectures",
        type=bool,
        default=False,
        help="Skip downloading lectures",
        action=LoadAction,
        nargs="?",
    )

    parser.add_argument(
        "--skip-articles",
        type=bool,
        default=False,
        help="Skip downloading articles",
        action=LoadAction,
        nargs="?",
    )

    parser.add_argument(
        "--skip-assignments",
        type=bool,
        default=False,
        help="Skip downloading assignments",
        action=LoadAction,
        nargs="?",
    )

    return parser
