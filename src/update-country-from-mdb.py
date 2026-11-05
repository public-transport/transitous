#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import sys

from mobilitydatabase import Database
from typing import Optional

region_file = sys.argv[1]
country_code = sys.argv[2]

mdb = Database.load()
relevant_entries = filter(lambda entry: entry["location.country_code"] == country_code, mdb.by_id.values())
# Handle static feeds first, so realtime feeds can pick up the name of their static feed
relevant_entries = sorted(relevant_entries, key=lambda entry: entry["data_type"] == "gtfs_rt")

with open(region_file, "r") as f:
    region = json.load(f)

    id_map = {}

    for source in region["sources"]:
        if "mdb-id" in source:
            id_map[source["mdb-id"]] = source

    for feed in relevant_entries:
        # Inactive feeds (usually expired) may still be usable with extend-calendar
        if feed["status"] not in ("active", "inactive"):
            continue

        def make_name(name: str, provider: str, feed_id: str):
            return (provider or name or feed_id).replace("/", "").replace("_", "-").replace(" ", "-").replace(",", "")[0:50]

        name = ""
        if "static_reference" in feed and feed["static_reference"]:
            # match name of static feed
            if id_map.get(feed["static_reference"]):
                name = id_map[feed["static_reference"]]["name"]
            else:
                res = mdb.by_id[feed["static_reference"]]
                name = make_name(res["name"], res["provider"], res["id"])
        else:
            name = make_name(feed["name"], feed["provider"], feed["id"])
            # Static feeds need unique names, otherwise their output files collide
            if feed["id"] not in id_map and any(s.get("name") == name for s in region["sources"]):
                name = f"{name[0:40]}-{feed['id']}"


        source = {
            #"name": name, # to update names 
            "type": "mobility-database",
            "mdb-id": feed["id"],
        }
        # Not really needed, just for easier reading of the result
        if feed["data_type"] == "gtfs_rt":
            source["spec"] = "gtfs-rt"
        elif feed["status"] == "inactive":
            source["extend-calendar"] = True

        if feed["id"] in id_map:
            id_map[feed["id"]].update(source)
        else:
            # so name attribute is first
            new_source = {
                "name": name
            }
            new_source.update(source)
            region["sources"].append(new_source)
            id_map[feed["id"]] = new_source

with open(region_file, "w") as f:
    json.dump(region, f, indent=4, ensure_ascii=False)
    f.write("\n")
