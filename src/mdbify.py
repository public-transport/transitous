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

id_mapping_file = "mobilitydatabase-mapping.csv"

if not Path(id_mapping_file).exists():
    table = requests.get("https://docs.google.com/spreadsheets/d/1Q96KDppKsn2khdrkraZCQ7T_qRSfwj7WsvqXvuMt4Bc/export?format=csv&gid=1787149399").text
    with open(id_mapping_file, "w") as f:
        f.write(table)

transitland_to_mdb = {}

with open(id_mapping_file, "r") as f:
    for row in csv.DictReader(f, delimiter=",", quotechar="\""):
        if "Transitland ID" in row and row["Transitland ID"].strip():
            transitland_to_mdb[row["Transitland ID"]] = row["mdb_source_id"]

mdb = Database.load()
url_to_id = {}
for feed in mdb.by_id.values():
    url_to_id[canonicalize_url(feed["urls.direct_download"])] = feed["id"]

atlas = Atlas.load(Path("transitland-atlas"))

region = json.load(open(sys.argv[1], "r"))

for source in region["sources"]:
    if source["type"] == "http":
        mdb_id = url_to_id.get(canonicalize_url(source["url"]))
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
        if source["transitland-atlas-id"] in transitland_to_mdb:
            mdb_id = transitland_to_mdb[source["transitland-atlas-id"]]
            if mdb_id:
                source["type"] = "mobility-database"
                source["mdb-id"] = f"mdb-{mdb_id}"
                source.pop("transitland-atlas-id", None)
        else:
            mdb_sources = atlas.sources_by_id(sourceFromJson(source))
            if not mdb_sources:
                continue
            mdb_source = mdb_sources[0]
            url = mdb_source.url
            mdb_id = url_to_id.get(canonicalize_url(url))
            if mdb_id:
                source["type"] = "mobility-database"
                source["mdb-id"] = mdb_id
                source.pop("transitland-atlas-id", None)


print(region)
with open(sys.argv[1], "w") as region_out:
    region_out.write(json.dumps(region, indent=4, ensure_ascii=False))
    region_out.write("\n")
