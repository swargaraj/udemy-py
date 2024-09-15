<div align="center">
    <h1>udemy-py 🎓</h1>
    <p>A python-based tool enabling users to fetch udemy course content and save it locally, allowing for offline access.</p>
    <img src="https://img.shields.io/badge/License-MIT-blue">
</div>


## Example Usage

```
python .\main.py --url "https://www.udemy.com/course/example-course" --key decryption_key --cookie /path/to/cookie.txt --concurrent 8 --captions en_US
```

## Advance Usage

```
usage: main.py [-h] [--id ID] [--url URL] [--key KEY] [--cookies COOKIES] [--load [LOAD]] [--save [SAVE]]
               [--concurrent CONCURRENT] [--captions CAPTIONS]

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
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
