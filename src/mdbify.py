#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mobilitydatabase import Database
from transitland import Atlas
from urllib.parse import urlparse
from pathlib import Path
from metadata import *

import json
import sys
import csv
import requests


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(scheme="https", netloc=parsed.netloc.strip("www.")).geturl()

mdb = Database.load()
url_to_id = {}
for feed in mdb.by_id.values():
    url_to_id[canonicalize_url(feed["urls.direct_download"])] = feed["id"]

atlas = Atlas.load(Path("transitland-atlas"))

region = json.load(open(sys.argv[1], "r"))

for source in region["sources"]:
    if source["type"] == "http":
        mdb_id = url_to_id.get(canonicalize_url(source["url"]))
        url_override = source.get("url-override")

        if not mdb_id and url_override:
            mdb_id = url_to_id.get(canonicalize_url(url_override))

        if mdb_id:
            source["type"] = "mobility-database"
            source["mdb-id"] = mdb_id
            source.pop("url", None)
    if source["type"] == "url":
        mdb_id = url_to_id.get(canonicalize_url(source["url"]))
        if mdb_id:
            source["type"] = "mobility-database"
            source["mdb-id"] = mdb_id
            source.pop("url", None)
            source.pop("spec", None)
    if source["type"] == "transitland-atlas":
        transitland_source = sourceFromJson(source)
        resolved_sources = atlas.sources_by_id(transitland_source)
        if not resolved_sources:
            continue
        resolved_source = resolved_sources[0]
        url = resolved_source.url
        mdb_id = url_to_id.get(canonicalize_url(url))
        if not mdb_id:
            mdb_id = url_to_id.get(canonicalize_url(transitland_source.url_override))

        if mdb_id:
            source["type"] = "mobility-database"
            source["mdb-id"] = mdb_id
            source.pop("transitland-atlas-id", None)


with open(sys.argv[1], "w") as region_out:
    region_out.write(json.dumps(region, indent=4, ensure_ascii=False))
    region_out.write("\n")
