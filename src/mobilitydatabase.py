# SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path
from typing import Dict, Optional
from metadata import UrlSource, HttpSource, Source, MobilityDatabaseSource, License
from utils import eprint
import sys
import requests
import csv
import os


class Database:
    by_id: Dict[int, dict]

    def __init__(self):
        self.by_id = {}

    @staticmethod
    def load() -> "Database":
        db = Database()

        path = Path("mobilitydatabase.csv")
        if not path.exists():
            eprint("Caching Mobility Database export at `mobilitydatabase.csv`…")
            resp = requests.get("https://storage.googleapis.com/storage/v1/b/mdb-csv/o/sources.csv?alt=media")

            if resp.status_code != 200:
                raise Exception("Failed to download Mobility Database export")

            tmppath = ".tmp-" + str(os.getpid()) + "-" + str(path)

            with open(tmppath, "w") as f:
                f.write(resp.text)
                os.rename(tmppath, path)

        with open(path) as f:
            for row in csv.DictReader(f, delimiter=",", quotechar="\""):
                db.by_id[int(row["mdb_source_id"])] = row

        return db

    def source_by_id(self, source: MobilityDatabaseSource) -> Optional[Source]:
        result: Optional[Source] = None
        feed = self.by_id.get(source.mdb_id)

        if not feed:
            eprint(f"Warning: Did not find requested id {source.mdb_id} in Mobility Database.")
            eprint("         Try deleting the cache at `mobilitydatabase.csv` if the feed was added recently.")
            return None

        match feed["data_type"]:
            case "gtfs":
                result = HttpSource()
                result.name = source.name
                result.url = feed["urls.direct_download"]
                result.cache_url = feed["urls.latest"]
                result.options = source.options
                result.spec = "gtfs"
                result.fix = source.fix
                result.skip = source.skip
                result.skip_reason = source.skip_reason
                result.drop_too_fast_trips = source.drop_too_fast_trips
                result.function = source.function
                result.drop_shapes = source.drop_shapes

                if source.url_override:
                    result.url_override = source.url_override

            case "gtfs-rt":
                result = UrlSource()
                result.name = source.name
                result.url = feed["urls.direct_download"]
                result.spec = "gtfs-rt"
                result.skip = source.skip
                result.skip_reason = source.skip_reason
            case _:
                eprint("Warning: Found MDB source that we can't handle:",
                       source.mdb_id)
                return None

        if "license" in feed:
            result.license = License()
            result.license.url = feed["license"]

        return result
