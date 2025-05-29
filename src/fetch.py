#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from metadata import TransitlandSource, MobilityDatabaseSource, HttpSource, \
    UrlSource, Source, Region
from pathlib import Path
from datetime import datetime, timezone
from utils import eprint
from zipfile import ZipFile
from typing import Optional, Any, Iterable, IO
from zoneinfo import ZoneInfo
from enum import Enum

import email.utils
import requests
import transitland
import mobilitydatabase
import json
import sys
import os
import subprocess
import shutil
import region_helpers
import io
import hashlib
import csv


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


def parse_gtfs_csv(f: IO) -> csv.DictReader:
    header = list(map(lambda h: h.strip(), next(csv.reader(f))))
    return csv.DictReader(f, delimiter=",",
                          quotechar='"', fieldnames=header)


def get_feed_timezone(zip_file: ZipFile) -> Optional[str]:
    if "agency.txt" not in zip_file.namelist():
        return None

    with zip_file.open("agency.txt", "r") as a:
        with io.TextIOWrapper(a) as at:
            feedinforeader = parse_gtfs_csv(at)
            for row in feedinforeader:
                if "agency_timezone" in row \
                        and row["agency_timezone"]:
                    return row["agency_timezone"].strip()

    return None


class FeedValidity(Enum):
    EXPIRED = 1
    IN_FUTURE = 2
    CURRENTLY_VALID = 3


def parse_gtfs_date(date: str, feed_timezone: ZoneInfo) -> datetime:
    return datetime.strptime(date.strip(), "%Y%m%d") \
        .replace(tzinfo=feed_timezone)


def check_feed_already_valid(feed_info: Iterable[dict],
                             feed_timezone: ZoneInfo) -> bool:
    if not feed_info:
        return True

    today = datetime.now(tz=feed_timezone)
    valid_entries = map(
        lambda row: "feed_start_date" not in row or
        not row["feed_start_date"] or
        parse_gtfs_date(row["feed_start_date"], feed_timezone) <= today,
        feed_info)
    return any(valid_entries)


def check_feed_not_expired(feed_info: Iterable[dict],
                           calendar: Iterable[dict],
                           calendar_dates: Iterable[dict],
                           feed_timezone: ZoneInfo):
    today = datetime.now(tz=feed_timezone)

    def feed_info_not_expired():
        valid_entries = map(
            lambda row:
                "feed_end_date" not in row or not row["feed_end_date"] or
                parse_gtfs_date(row["feed_end_date"], feed_timezone) >= today,
            feed_info)
        return all(valid_entries)

    def calendar_not_expired():
        valid_entries = map(
            lambda row:
                parse_gtfs_date(row["end_date"], feed_timezone) >= today,
            calendar)
        return any(valid_entries)

    def calendar_dates_not_expired():
        valid_entries = map(
            lambda row:
                parse_gtfs_date(row["date"], feed_timezone) >= today,
            calendar_dates)
        return any(valid_entries)

    return feed_info_not_expired() and \
        (calendar_not_expired() or calendar_dates_not_expired())


def check_feed_timeframe_valid(zip_file: ZipFile) -> FeedValidity:
    def read_file(name: str) -> Iterable[dict]:
        if name not in zip_file.namelist():
            return []

        a = zip_file.open(name, "r")
        at = io.TextIOWrapper(a)
        return parse_gtfs_csv(at)

    feed_info = read_file("feed_info.txt")
    calendar = read_file("calendar.txt")
    calendar_dates = read_file("calendar_dates.txt")

    tz = get_feed_timezone(zip_file)

    if not tz:
        raise Exception("Could not check validity, because the time zone could not be detected")

    feed_timezone = ZoneInfo(tz)

    if not check_feed_already_valid(feed_info, feed_timezone):
        return FeedValidity.IN_FUTURE

    if not check_feed_not_expired(feed_info, calendar, calendar_dates,
                                  feed_timezone):
        return FeedValidity.EXPIRED

    return FeedValidity.CURRENTLY_VALID


def download_http_source(
    dest_path: Path, source: HttpSource,
        session=requests.Session()) -> Optional[requests.Response]:
    """
    Performs the download of the source and returns the response.
    The urls will be tried in the following order: url_override, url, cache_url
    """
    request_options: dict[str, Any] = {
        "verify": not source.options.ignore_tls_errors,
        "timeout": 30
    }

    headers = source.options.headers.copy()
    if "user-agent" not in headers:
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
        return None

    urls_to_try: list[tuple[str, str]] = []
    # tuple unpacking needed to appease mypy
    for name, url in [
        ("url-override", source.url_override),
        ("url", source.url),
        ("cache-url", source.cache_url)
    ]:
        if url:
            urls_to_try.append((name, url))

    primary_url_name, primary_url = urls_to_try[0]

    errors = []
    while urls_to_try:
        name, url = urls_to_try.pop(0)
        try:
            # Fetch last modification time from the server
            server_headers = \
                session.head(url, headers=headers,
                             allow_redirects=True,
                             **request_options).headers

            # If server version is older, return
            last_modified_server = None
            if "last-modified" in server_headers:
                last_modified_server = email.utils.parsedate_to_datetime(
                    server_headers["last-modified"])

                if last_modified and last_modified_server <= last_modified:
                    return None

            # Tell the server not to send data if it is older
            # than what we have
            if last_modified:
                headers["if-modified-since"] = last_modified \
                    .strftime("%a, %d %b %Y %X %Z")

            response = session.get(url, headers=headers,
                                   **request_options)

            # If the file was not modified, return
            if response.status_code == 304:
                return None

            # If the file was not successfully retrieved, throw
            if response.status_code != 200:
                raise Exception(f"Could not fetch file. HTTP Status code: {response.status_code}")

            # Try if response was zip
            # (some servers return html error page with code 200)
            ZipFile(io.BytesIO(response.content))

            # all errors checked, it worked
            if name != primary_url_name:
                eprint(f"Warning: Used {name} instead of {primary_url_name} ({primary_url}) because it was not reachable")

            return response
        except Exception as e:
            errors.append((name, e))

    raise Exception(errors)


class Fetcher:
    transitland_atlas: transitland.Atlas

    def __init__(self):
        self.transitland_atlas = transitland.Atlas.load(
            Path("transitland-atlas/"))
        self.mobility_database = None

    # Returns whether something was downloaded
    def fetch_source(self, dest_path: Path, source: Source) -> bool:
        if source.spec != "gtfs" and source.spec != "gtfs-flex":
            return False
        match source:
            case TransitlandSource():
                http_source = self.transitland_atlas.source_by_id(source)
                if not http_source:
                    eprint("Error: Could not resolve", source.transitland_atlas_id)
                    sys.exit(1)

                return self.fetch_source(dest_path, http_source)
            case MobilityDatabaseSource():
                if not self.mobility_database:
                    self.mobility_database = mobilitydatabase.Database.load()
                http_source = self.mobility_database.source_by_id(source)
                if not http_source:
                    eprint("Error: Could not resolve", source.mdb_id)
                    sys.exit(1)

                return self.fetch_source(dest_path, http_source)
            case HttpSource():
                response = download_http_source(dest_path, source)

                # No request was made
                if not response:
                    return False

                last_modified_server = None

                # Update our last_modified_server information from the response
                # of the actual download.
                server_headers = response.headers
                if "last-modified" in server_headers:
                    last_modified_server = email.utils.parsedate_to_datetime(
                        server_headers["last-modified"])

                content: bytes
                if "#" in source.url and source.url.partition("#")[2]:
                    # if URL contains #, treat the path after # as an embedded ZIP file
                    sub_path = source.url.partition("#")[2]
                    zipfile = ZipFile(io.BytesIO(response.content))

                    content = zipfile.read(sub_path)
                else:
                    content = response.content

                # Only write file if the new version changed. Helps to at least
                # skip postprocessing with servers that don't send a
                # last-modified header.
                if dest_path.exists() and not last_modified_server:
                    h = hashlib.new("sha256")
                    h.update(content)
                    digest = h.hexdigest()

                    with open(dest_path, "rb") as tfp:
                        new_digest = hashlib.file_digest(tfp, "sha256") \
                            .hexdigest()

                    if digest == new_digest:
                        return False

                with open(dest_path, "wb") as dest:
                    dest.write(content)

                # Set server mtime on local file
                if last_modified_server:
                    atime_mtime = (last_modified_server.timestamp(),
                                   last_modified_server.timestamp())
                    os.utime(dest_path, atime_mtime)

                return True
            case UrlSource():
                return False

        eprint("Unknown data source", source, file=sys.stderr)
        assert False

    def postprocess(self, source: Source,
                    input_path: Path, output_path: Path):
        temp_file = output_path.parent / f".tmp-{output_path.name}"
        shutil.copyfile(input_path, temp_file)

        if source.fix_csv_quotes:
            subprocess.check_call(["./src/fix-csv-quotes.py", temp_file])

        if source.spec != "gtfs-flex":
            # gtfsclean can't handle GTFS-Flex data and would discard it entirely
            command = ["gtfsclean", str(temp_file),
                    "--fix-zip",
                    "--check-null-coords",
                    "--empty-agency-url-repl", "https://transitous.org",
                    "--remove-red-services",
                    "--output", str(temp_file)]
            if source.fix:
                command.append("--fix")
            if source.drop_too_fast_trips:
                command.append("--drop-too-fast-trips")
            if source.drop_shapes:
                command.append("--drop-shapes")
            if source.drop_agency_names:
                for agency in source.drop_agency_names:
                    command.append("--drop-agency-names")
                    command.append(agency)
            if source.display_name_options:
                if source.display_name_options.copy_trip_names_matching:
                    command.append("--copy-trip-names-matching")
                    command.append(source.display_name_options.copy_trip_names_matching)
                if source.display_name_options.keep_route_names_matching:
                    command.append("--keep-route-names-matching")
                    command.append(source.display_name_options.keep_route_names_matching)
                if source.display_name_options.move_headsigns_matching:
                    command.append("--move-headsigns-matching")
                    command.append(source.display_name_options.move_headsigns_matching)

            subprocess.check_call(command)

        with ZipFile(file=open(temp_file, "rb")) as z:
            validity = check_feed_timeframe_valid(z)
            if validity == FeedValidity.IN_FUTURE and output_path.exists():
                eprint("Info: Feed not yet valid, using old version")
                os.remove(temp_file)
                os.remove(input_path)  # to force checking again
                return

            if validity == FeedValidity.EXPIRED:
                eprint("Error: Feed is expired, please consider " +
                       "removing or updating its source")
                raise Exception("Feed is expired")

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
                    http_source = self.transitland_atlas.source_by_id(source)

                    # Transitland source type that we cannot handle
                    if not http_source:
                        continue

                    source = http_source

            validate_source_name(source.name)
            download_name = f"{region_name}_{source.name}"

            print(f"Fetching {region_name}-{source.name}…")
            sys.stdout.flush()

            # Nothing to download for realtime feeds
            if source.spec != "gtfs" and source.spec != "gtfs-flex":
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
