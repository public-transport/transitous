# SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path
from typing import Dict, Optional
from metadata import UrlSource, HttpSource, Source, MobilityDatabaseSource, License, inherit_options_from_db_source
from license_expression import get_spdx_licensing, ExpressionError, Licensing
from utils import eprint
import requests
import csv
import os
import urllib


class Database:
    by_id: Dict[str, dict]
    licensing: Licensing

    def __init__(self):
        self.by_id = {}
        self.licensing = get_spdx_licensing()

    @staticmethod
    def url_to_spdx(licensing: Licensing, url: str) -> Optional[str]:
        parsed = urllib.parse.urlparse(url)
        spdx_identifier = None

        if parsed.hostname == "creativecommons.org":
            path = iter(parsed.path.split("/"))
            try:
                next(path)
                dir = next(path)

                if dir == "licenses":
                    cc_type = next(path).upper()
                    version = next(path)
                    document = next(path)
                    country = None

                    if not document.startswith("deed"):
                        country = document.upper()

                    if country:
                        spdx_identifier = f"CC-{cc_type}-{version}-{country}"
                    else:
                        spdx_identifier = f"CC-{cc_type}-{version}"
                elif dir == "publicdomain":
                    cc_type = next(path)
                    version = next(path)
                    document = next(path)

                    if document.startswith("deed"):
                        match cc_type:
                            case "zero":
                                spdx_identifier = f"CC0-{version}"
            except StopIteration:
                pass
        elif parsed.hostname == "opendatacommons.org":
            if parsed.path.strip("/") == "licenses/odbl" or parsed.path.strip("/") == "licenses/odbl/1.0":
                spdx_identifier = "ODbL-1.0"

        try:
            licensing.validate_license_keys(licensing.parse(spdx_identifier))
        except ExpressionError as e:
            spdx_identifier = None

        return spdx_identifier


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

    def redirect_by_id(self, mdb_id: str) -> Optional[str]:
        row = self.by_id.get(mdb_id)
        if not row:
            return None

        return row.get("redirect.id")

    def source_by_id(self, source: MobilityDatabaseSource) -> Optional[Source]:
        result: Optional[Source] = None
        feed = self.by_id.get(source.mdb_id)

        if not feed:
            eprint(f"Warning: Did not find requested id {source.mdb_id} in Mobility Database.")
            eprint("         Try deleting the cache at `mobilitydatabase.csv` if the feed was added recently.")
            return None

        match feed["data_type"]:
            case "gtfs":
                result = inherit_options_from_db_source(source)
                result.url = feed["urls.direct_download"]
                result.cache_url = feed["urls.latest"]
                result.spec = "gtfs"
            case "gtfs_rt":
                result = UrlSource()
                result.name = source.name
                if source.url_override:
                    result.url = source.url_override
                else:
                    result.url = feed["urls.direct_download"]
                result.spec = "gtfs-rt"
                result.skip = source.skip
                result.skip_reason = source.skip_reason
                result.use_feed_proxy = source.use_feed_proxy
            case data_type:
                eprint("Warning: Found MDB source that we can't handle:",
                       source.mdb_id, "of type", data_type)
                return None

        result.license = License()

        if "urls.license" in feed and feed["urls.license"]:
            result.license.url = feed["urls.license"]
            result.license.spdx_identifier = Database.url_to_spdx(self.licensing, feed["urls.license"])

        # Allow to override these as mobility database does not have spdx-identifiers (yet)
        if source.license.spdx_identifier:
            result.license.spdx_identifier = source.license.spdx_identifier
        if source.license.url:
            result.license.url = source.license.url

        return result
