#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from mobilitydatabase import Database

import json
import sys

mdb = Database.load()
region = json.load(open(sys.argv[1], "r"))

for source in region["sources"]:
    if source["type"] == "mobility-database":
        mdb_id = source.get("mdb-id")
        new_id = mdb.redirect_by_id(mdb_id)
        if new_id:
            source["mdb-id"] = new_id

with open(sys.argv[1], "w") as region_out:
    region_out.write(json.dumps(region, indent=4, ensure_ascii=False))
    region_out.write("\n")
