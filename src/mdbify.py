#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mobilitydatabase import Database
from urllib.parse import urlparse

import json
import sys


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(scheme="https", netloc=parsed.netloc.strip("www.")).geturl()


mdb = Database.load()
url_to_id = {}
for feed in mdb.by_id.values():
    url_to_id[canonicalize_url(feed["urls.direct_download"])] = feed["id"]

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


print(region)
with open(sys.argv[1], "w") as region_out:
    region_out.write(json.dumps(region, indent=4, ensure_ascii=False))
    region_out.write("\n")
