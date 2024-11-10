<div align="center">
    <h1>udemy-py 🎓</h1>
    <p>A python-based tool enabling users to fetch udemy course content and save it locally, allowing for offline access.</p>
    <img src="https://img.shields.io/badge/License-MIT-blue">
    <img src="https://img.shields.io/github/contributors/swargaraj/udemy-py">
    <img src="https://img.shields.io/github/issues/swargaraj/udemy-py">
    <img src="https://img.shields.io/github/v/release/swargaraj/udemy-py">
</div>

> [!CAUTION]
> Downloading and decrypting content from Udemy without proper authorization or in violation of their terms of service is illegal and unethical. By using this tool, you agree to comply with all applicable laws and respect the intellectual property rights of content creators. The creator of this tool is not responsible for any illegal use or consequences arising from the use of this software.

## Requirements

To use this tool, you need to install some third-party software and Python modules. Follow the instructions below to set up your environment:

### Third-Party Software

1. [FFmpeg](https://www.ffmpeg.org/download.html): This tool is required for handling multimedia files. You can download it from FFmpeg's official website and follow the installation instructions specific to your operating system.
2. [n_m3u8_dl-re](https://github.com/nilaoda/N_m3u8DL-RE/releases): This tool is used for downloading and processing m3u8 & mpd streams. Make sure to rename the downloaded binary to n_m3u8_dl-re (case-sensitive) for compatibility with this tool. You can find it on their GitHub.
3. [MP4 Decrypt](https://www.bento4.com/downloads/): This software is necessary for decrypting MP4 files. You can download their SDK from their official site.

### Python Modules

Install the required Python modules using the following command:

```bash
pip install -r requirements.txt
```

Make sure you have a working Python environment and pip installed to handle the dependencies listed in requirements.txt.

## Getting Started

To use this tool, you'll need to set up a few prerequisites:

### Udemy Cookies

You need to provide Udemy cookies to authenticate your requests. To extract these cookies:

- Use the [Cookie Editor extension](https://cookie-editor.com/) (available for Chrome or Firefox).
- Extract the cookies as a Netscape format.
- Save the extracted cookies as `cookies.txt` and place this file in the same directory where you execute the tool.

### Decryption Key

If you're dealing with DRM-protected videos, you'll need a decryption key. This key is essential for decrypting such content.
> [!WARNING]
> No guidance or assistance on obtaining the decryption key will be provided, as circumventing DRM protection is illegal. Ensure you comply with all applicable laws and respect intellectual property rights.

## Example Usage

```bash
python .\main.py --url "https://www.udemy.com/course/example-course" --key decryption_key --cookies /path/to/cookies.txt --concurrent 8 --captions en_US
```

## Advance Usage

```bash
usage: main.py [-h] [--id ID] [--url URL] [--portal PORTAL] [--key KEY] [--cookies COOKIES] [--load [LOAD]] [--save [SAVE]]
               [--concurrent CONCURRENT] [--start-chapter START_CHAPTER] [--start-lecture START_LECTURE]
               [--end-chapter END_CHAPTER] [--end-lecture END_LECTURE] [--captions CAPTIONS] [--srt [SRT]] [--tree [TREE]]
               [--skip-captions [SKIP_CAPTIONS]] [--skip-assets [SKIP_ASSETS]] [--skip-lectures [SKIP_LECTURES]]
               [--skip-articles [SKIP_ARTICLES]] [--skip-assignments [SKIP_ASSIGNMENTS]]

Udemy Course Downloader

options:
  -h, --help            show this help message and exit
  --id, -i ID           The ID of the Udemy course to download
  --url, -u URL         The URL of the Udemy course to download
  --portal, -p PORTAL   The portal of the Udemy account
  --key, -k KEY         Key to decrypt the DRM-protected videos
  --cookies, -c COOKIES
                        Path to cookies.txt file
  --load, -l [LOAD]     Load course curriculum from file
  --save, -s [SAVE]     Save course curriculum to a file
  --concurrent, -cn CONCURRENT
                        Maximum number of concurrent downloads
  --start-chapter START_CHAPTER
                        Start the download from the specified chapter
  --start-lecture START_LECTURE
                        Start the download from the specified lecture
  --end-chapter END_CHAPTER
                        End the download at the specified chapter
  --end-lecture END_LECTURE
                        End the download at the specified lecture
  --captions CAPTIONS   Specify what captions to download. Separate multiple captions with commas
  --srt [SRT]           Convert the captions to srt format
  --tree [TREE]         Create a tree view of the course curriculum
  --skip-captions [SKIP_CAPTIONS]
                        Skip downloading captions
  --skip-assets [SKIP_ASSETS]
                        Skip downloading assets
  --skip-lectures [SKIP_LECTURES]
                        Skip downloading lectures
  --skip-articles [SKIP_ARTICLES]
                        Skip downloading articles
  --skip-assignments [SKIP_ASSIGNMENTS]
                        Skip downloading assignments
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
