#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from metadata import *
from pathlib import Path
from datetime import datetime, timezone
from utils import eprint

import email.utils
import requests
import transitland
import json
import sys
import os
import subprocess
import shutil
import region_helpers


def validate_source_name(name: str):
    if " " in name:
        eprint(f"Error: Feed names must not contain spaces, found {name}.")
        sys.exit(1)

    if "_" in name:
        eprint(f"Error: Feed names must not contain underscores, found {name}.")
        sys.exit(1)

    if "/" in name:
        eprint(f"Error: Feed names must not contain slashes, found {name}.")
        sys.exit(1)


class Fetcher:
    transitland_atlas: transitland.Atlas

    def __init__(self):
        self.transitland_atlas = transitland.Atlas.load(
            Path("transitland-atlas/"))

    # Returns whether something was downloaded
    def fetch_source(self, dest_path: Path, source: Source) -> bool:
        if source.spec != "gtfs":
            return False
        match source:
            case TransitlandSource():
                http_source = self.transitland_atlas.source_by_id(source)
                if not http_source:
                    sys.exit(1)

                return self.fetch_source(dest_path, http_source)
            case HttpSource():
                request_options = {
                    "verify": not source.options.ignore_tls_errors
                }

                headers = source.options.headers.copy()
                headers["user-agent"] \
                    = "Transitous GTFS Fetcher (https://transitous.org)"

                # Detect last modification time of local file
                last_modified = None
                if dest_path.exists():
                    mtime = dest_path.stat().st_mtime
                    last_modified = datetime.fromtimestamp(mtime,
                                                           tz=timezone.utc)

                # Check if the last download was longer than the interval ago
                if source.options.fetch_interval_days and last_modified \
                        and (datetime.now(tz=timezone.utc) - last_modified).days \
                        < source.options.fetch_interval_days:
                    return False

                download_url = source.url_override if source.url_override else source.url

                # Fetch last modification time from the server
                server_headers = \
                    requests.head(download_url, headers=headers,
                                  allow_redirects=True,
                                  **request_options).headers

                # If server version is older, return
                last_modified_server = None
                if "last-modified" in server_headers:
                    last_modified_server = email.utils.parsedate_to_datetime(
                        server_headers["last-modified"])

                    if last_modified and last_modified_server <= last_modified:
                        return False

                # Tell the server not to send data if it is older
                # than what we have
                if last_modified:
                    headers["if-modified-since"] = last_modified \
                        .strftime("%a, %d %b %Y %X %Z")

                response = requests.get(download_url, headers=headers,
                                        **request_options)

                # If the file was not modified, return
                if response.status_code == 304:
                    return False

                # If the file was not successfully retrieved, return
                if response.status_code != 200:
                    print("Error: Could not fetch file:")
                    print("Status Code:", response.status_code,
                          "Body:", response.content)
                    raise Exception()

                # Update our last_modified_server information from the response
                # of the actual download. The values of the head request can
                # differ, if the response of the head request is a redirect.
                # The redirect then usually has no last-modified information,
                # but the actual target does.
                server_headers = response.headers
                if "last-modified" in server_headers:
                    last_modified_server = email.utils.parsedate_to_datetime(
                        server_headers["last-modified"])

                with open(dest_path, "wb") as dest:
                    dest.write(response.content)

                # Set server mtime on local file
                if last_modified_server:
                    atime_mtime = (last_modified_server.timestamp(),
                                   last_modified_server.timestamp())
                    os.utime(dest_path, atime_mtime)

                return True
            case UrlSource():
                return False

        print("Unknown data source", source, file=sys.stderr)
        assert False

    def postprocess(self, source: Source,
                    input_path: Path, output_path: Path):
        temp_file = output_path.parent / f".tmp-{output_path.name}"
        shutil.copyfile(input_path, temp_file)

        if source.fix_csv_quotes:
            subprocess.check_call(["./src/fix-csv-quotes.py", temp_file])

        command = ["gtfsclean", str(temp_file),
                   "--fix-zip",
                   "--check-null-coords",
                   "--empty-agency-url-repl", "https://transitous.org",
                   "--remove-red-routes", "--remove-red-services", "--remove-red-stops", "--remove-red-trips", "--red-trips-fuzzy",
                   "--output", str(temp_file)]
        if source.fix:
            command.append("--fix")

        subprocess.check_call(command)

        os.rename(temp_file, output_path)

    def fetch(self, metadata: Path):
        region = Region(json.load(open(metadata, "r")))
        metadata_filename = metadata.name
        region_name = metadata_filename[:metadata_filename.rfind('.')]

        errors = 0

        outdir = Path("out/")
        if not outdir.exists():
            os.mkdir(outdir)

        for source in region.sources:
            if source.function:
                source = getattr(region_helpers, source.function)(source)

            if source.skip:
                if source.skip_reason != "":
                    print("Skipping " + source.name + ": " + source.skip_reason)
                else:
                    print("Skipping " + source.name)
                continue
            # Resolve transitland sources to http / url sources
            match source:
                case TransitlandSource():
                    source = self.transitland_atlas.source_by_id(source)

                    # Transitland source type that we cannot handle
                    if not source:
                        continue

            validate_source_name(source.name)
            download_name = f"{region_name}_{source.name}"

            print(f"Fetching {region_name}-{source.name}…")
            sys.stdout.flush()

            # Nothing to download for realtime feeds
            if source.spec != "gtfs":
                continue

            download_dir = Path("downloads/")
            if not download_dir.exists():
                os.mkdir(download_dir)

            download_path = download_dir.absolute() / f"{download_name}.gtfs.zip"
            output_path = outdir.absolute() / f"{download_name}.gtfs.zip"

            try:
                new_data = self.fetch_source(download_path, source)
            except Exception as e:
                eprint(f"Error: Could not fetch {region_name}-{source.name}: {e}")
                errors += 1
                continue

            # Nothing new was downloaded, and data is already processed
            if not new_data and output_path.exists():
                continue

            # Something new was downloaded or the data was previously not processed
            print(f"Postprocessing {region_name}-{source.name} with gtfstidy…")
            sys.stdout.flush()

            try:
                self.postprocess(source, download_path, output_path)
            except Exception as e:
                eprint(f"Error: Could not postprocess {region_name}-{source.name}: {e}")
                errors += 1
                continue

            print()
            sys.stdout.flush()

        return errors

if __name__ == "__main__":
    fetcher = Fetcher()

    metadata_file = sys.argv[1]
    errors = fetcher.fetch(Path(metadata_file))
    if errors > 0:
        eprint(f"Error: {errors} errors occurred during fetching.")
        sys.exit(1)
