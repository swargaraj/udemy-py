from dataclasses import dataclass
from typing import Optional


@dataclass
class UdemySettings:
    course_url: str
    key: str
    portal: str
    cookie_path: str
    captions: bool
    skip_captions: bool
    skip_assets: bool
    skip_lectures: bool
    skip_articles: bool
    skip_assignments: bool
    convert_to_srt: bool


@dataclass
class DownloadSettings:
    max_concurrent_lectures: int
    start_chapter: Optional[int] = None
    end_chapter: Optional[int] = None
    start_lecture: Optional[int] = None
    end_lecture: Optional[int] = None
