#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

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
                http_source = self.transitland_atlas.source_by_id(source)
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

        print("Unknown data source", source, file=sys.stderr)
        assert False

    def postprocess(self, source: Source, path: Path):
        tmpdir = Path("transitious-gtfs-tmpdir")
        outdir = Path("out")

        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

        os.mkdir(tmpdir)

        if not os.path.exists(outdir):
            os.mkdir(outdir)

        output_file_path = str(outdir.absolute() / path.name)

        command = ["gtfstidy", str(path.absolute()), "--output", output_file_path]
        if source.fix:
            command.append("--fix")

        subprocess.call(command, cwd=tmpdir)

        shutil.rmtree(tmpdir)

    def fetch(self, metadata: Path):
        region = Region(json.load(open(metadata, "r")))
        metadata_filename = metadata.name
        region_name = metadata_filename[:metadata_filename.rfind('.')]

        for source in region.sources:
            download_name = f"{region_name}_{source.name}"

            print(f"Fetching {region_name}-{source.name}…")
            sys.stdout.flush()
            dest_path = self.fetch_source(download_name, source)

            print(f"Postproccing {region_name}-{source.name} with gtfstidy…")
            sys.stdout.flush()
            self.postprocess(source, dest_path)

            print()
            sys.stdout.flush()


if __name__ == "__main__":
    fetcher = Fetcher()

    metadata_file = sys.argv[1]
    fetcher.fetch(Path(metadata_file))
