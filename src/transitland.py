from pathlib import Path
from typing import Dict
import json
from metadata import *


class Atlas:
    by_id: Dict[str, dict]

    def __init__(self):
        self.by_id = {}

    @staticmethod
    def load(path: Path):
        atlas = Atlas()
        for f in Path(path / "feeds").iterdir():
            for feed in json.load(open(f, "r"))["feeds"]:
                atlas.by_id[feed["id"]] = feed

        return atlas

    def source_by_id(self, feed_id: str) -> HttpSource:
        feed = self.by_id[feed_id]
        http_source = HttpSource()
        http_source.url = feed["urls"]["static_current"]
        return http_source
