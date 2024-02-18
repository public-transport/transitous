#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from metadata import *
from pathlib import Path
from datetime import datetime

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

    def fetch_source(self, name: str, source: Source) -> Optional[Path]:
        if source.spec != "gtfs":
            return None
        match source:
            case TransitlandSource():
                http_source = self.transitland_atlas.source_by_id(source)
                return self.fetch_source(name, http_source)
            case HttpSource():
                # Detect last modification time of local file
                last_modified = None
                dest_path = Path(f"downloads/{name}.gtfs.zip")
                if dest_path.exists():
                    mtime = dest_path.stat().st_mtime
                    last_modified = datetime.fromtimestamp(mtime)

                # Check if the last download was longer than the interval ago
                if source.options.fetch_interval_days and last_modified \
                        and (datetime.now() - last_modified).days \
                        < source.options.fetch_interval_days:
                    return None

                # Fetch last modification time from the server
                server_headers = requests.head(source.url).headers

                # If server version is older, return
                last_modified_server = None
                if "last-modified" in server_headers:
                    last_modified_server = datetime.strptime(
                        server_headers["last-modified"], "%a, %d %b %Y %X %Z")

                    if last_modified and last_modified_server <= last_modified:
                        return None

                # Tell the server not to send data if it is older
                # than what we have
                headers = {}
                if last_modified:
                    headers["if-modified-since"] = last_modified \
                        .strftime("%a, %d %b %Y %X %Z")

                response = requests.get(source.url, headers=headers)

                # If the file was not modified, return
                if response.status_code == 304:
                    return None

                # If the file was not successfully retrieved, return
                if response.status_code != 200:
                    return None

                download_dir = "downloads"

                if not os.path.exists(download_dir):
                    os.mkdir(download_dir)

                with open(dest_path, "wb") as dest:
                    dest.write(response.content)

                # Set server mtime on local file
                if last_modified_server:
                    atime_mtime = (last_modified_server.timestamp(),
                                   last_modified_server.timestamp())
                    os.utime(dest_path, atime_mtime)

                return dest_path
            case UrlSource():
                return None

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

            # Nothing was downloaded
            if not dest_path:
                continue

            print(f"Postproccing {region_name}-{source.name} with gtfstidy…")
            sys.stdout.flush()
            self.postprocess(source, dest_path)

            print()
            sys.stdout.flush()


if __name__ == "__main__":
    fetcher = Fetcher()

    metadata_file = sys.argv[1]
    fetcher.fetch(Path(metadata_file))
