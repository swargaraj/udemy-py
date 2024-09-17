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
1. FFmpeg: This tool is required for handling multimedia files. You can download it from [FFmpeg's official website](https://www.ffmpeg.org/download.html) and follow the installation instructions specific to your operating system.
2. n_m3u8_dl-re: This tool is used for downloading and processing m3u8 & mpd streams. You can find it on GitHub at [n_m3u8_dl-re](https://github.com/nilaoda/N_m3u8DL-RE/releases). Make sure to rename the downloaded binary to n_m3u8_dl-re (case-sensitive) for compatibility with this tool.
3. MP4 Decrypt: This software is necessary for decrypting MP4 files. You can download their SDK from their [official site](https://www.bento4.com/downloads/).

### Python Modules
Install the required Python modules using the following command:
```
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

```
python .\main.py --url "https://www.udemy.com/course/example-course" --key decryption_key --cookies /path/to/cookie.txt --concurrent 8 --captions en_US
```

## Advance Usage

```
usage: main.py [-h] [--id ID] [--url URL] [--key KEY] [--cookies COOKIES] [--load [LOAD]] [--save [SAVE]] [--concurrent CONCURRENT]
               [--captions CAPTIONS] [--tree [TREE]] [--skip-captions [SKIP_CAPTIONS]] [--skip-assets [SKIP_ASSETS]]
               [--skip-lectures [SKIP_LECTURES]] [--skip-articles [SKIP_ARTICLES]] [--skip-assignments [SKIP_ASSIGNMENTS]]

Udemy Course Downloader

options:
  -h, --help            show this help message and exit
  --id ID, -i ID        The ID of the Udemy course to download
  --url URL, -u URL     The URL of the Udemy course to download
  --key KEY, -k KEY     Key to decrypt the DRM-protected videos
  --cookies COOKIES, -c COOKIES
                        Path to cookies.txt file
  --load [LOAD], -l [LOAD]
                        Load course curriculum from file
  --save [SAVE], -s [SAVE]
                        Save course curriculum to a file
  --concurrent CONCURRENT, -cn CONCURRENT
                        Maximum number of concurrent downloads
  --captions CAPTIONS   Specify what captions to download. Separate multiple captions with commas
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
