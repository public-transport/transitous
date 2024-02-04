from metadata import *
from pathlib import Path
import requests
import transitland
import json
import sys
import os
import subprocess
import shutil

class Fetcher:
    transitland_atlas: transitland.Atlas

    def __init__(self):
        self.transitland_atlas = transitland.Atlas.load(
            Path("transitland-atlas/"))

    def fetch_source(self, name: str, source: Source) -> Path:
        match source:
            case TransitlandSource():
                http_source = self.transitland_atlas.source_by_id(source.transitland_atlas_id)
                return self.fetch_source(name, http_source)
            case HttpSource():
                content = requests.get(source.url).content
                download_dir = "downloads"

                if not os.path.exists(download_dir):
                    os.mkdir(download_dir)

                dest_path = Path(f"downloads/{name}.gtfs.zip")
                with open(dest_path, "wb") as dest:
                    dest.write(content)

                return dest_path

        print("Uknown data source", source, file=sys.stderr)
        assert False

    def postprocess(self, path: Path):
        tmpdir = Path("transitious-gtfs-tmpdir")
        outdir = Path("out")

        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

        os.mkdir(tmpdir)

        if not os.path.exists(outdir):
            os.mkdir(outdir)

        output_file_path = str(outdir.absolute() / path.name)

        subprocess.call(["gtfstidy", str(path.absolute()), "--output", output_file_path], cwd=tmpdir)

        shutil.rmtree(tmpdir)

    def fetch(self, metadata: Path):
        region = Region.fromJson(json.load(open(metadata, "r")))

        i = 0
        for source in region.sources:
            metadata_filename = metadata.name
            region_name = metadata_filename[:metadata_filename.rfind('.')]
            download_name = f"{region_name}_{i}"

            print(f"Fetching {region_name}…")

            dest_path = self.fetch_source(download_name, source)

            print(f"Postproccing {region_name} with gtfstidy…")
            self.postprocess(dest_path)

            i += 1


if __name__ == "__main__":
    fetcher = Fetcher()

    metadata_file = sys.argv[1]
    fetcher.fetch(Path(metadata_file))
