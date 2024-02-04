from metadata import *
from pathlib import Path
import requests
import transitland
import json
import sys


class Fetcher:
    transitland_atlas: transitland.Atlas

    def __init__(self):
        self.transitland_atlas = transitland.Atlas.load(Path("transitland-atlas/"))

    def fetch_source(self, source: Source):
        match source:
            case TransitlandSource():
                http_source = self.transitland_atlas.source_by_id(source.transitland_atlas_id)
                self.fetch_source(http_source)
            case HttpSource():
                requests.get(source.url)

    def fetch(self, metadata: Path):
        region = Region.fromJson(json.load(open(metadata, "r")))
        for source in region.sources:
            self.fetch_source(source)


if __name__ == "__main__":
    fetcher = Fetcher()

    metadata_file = sys.argv[1]
    fetcher.fetch(Path(metadata_file))
