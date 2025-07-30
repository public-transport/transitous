# SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path
from typing import Dict, Optional
from metadata import UrlSource, HttpSource, Source, MobilityDatabaseSource, License, inherit_options_from_db_source
from utils import eprint
import requests
import csv
import os


class Database:
    by_id: Dict[str, dict]

    def __init__(self):
        self.by_id = {}

    @staticmethod
    def load() -> "Database":
        db = Database()

        path = Path("mobilitydatabase.csv")
        if not path.exists():
            eprint("Caching Mobility Database export at `mobilitydatabase.csv`…")
            resp = requests.get("https://files.mobilitydatabase.org/feeds_v2.csv")

            if resp.status_code != 200:
                raise Exception("Failed to download Mobility Database export")

            tmppath = ".tmp-" + str(os.getpid()) + "-" + str(path)

            with open(tmppath, "w") as f:
                f.write(resp.text)
                os.rename(tmppath, path)

        with open(path) as f:
            for row in csv.DictReader(f, delimiter=",", quotechar="\""):
                db.by_id[row["id"]] = row

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
                result.fix_csv_quotes = source.fix_csv_quotes
                result.display_name_options = source.display_name_options

                if source.url_override:
                    result.url_override = source.url_override

            case "gtfs_rt":
                result = UrlSource()
                result.name = source.name
                result.url = feed["urls.direct_download"]
                result.spec = "gtfs-rt"
                result.skip = source.skip
                result.skip_reason = source.skip_reason
            case data_type:
                eprint("Warning: Found MDB source that we can't handle:",
                       source.mdb_id, "of type", data_type)
                return None

        result.license = License()

        if "license" in feed:
            result.license.url = feed["license"]

        # Allow to override these as mobility database does not have spdx-identifiers (yet)
        if source.license.spdx_identifier:
            result.license.spdx_identifier = source.license.spdx_identifier
        if source.license.url:
            result.license.url = source.license.url

        return result
