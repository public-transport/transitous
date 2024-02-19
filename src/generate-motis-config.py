#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess
import json
import metadata
import tomllib
import sys

from pathlib import Path
from jinja2 import Template


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("First argument must be one of import, full")
        sys.exit(1)

    flavour = sys.argv[1]

    feed_dir = Path("feeds/")
    osm_map = "berlin-latest.osm.pbf"

    gtfs_feeds = []
    gtfsrt_feeds = []

    for feed in feed_dir.glob("*.json"):
        with open(feed, "r") as f:
            parsed = json.load(f)
            region = metadata.Region(parsed)

            metadata_filename = feed.name
            region_name = metadata_filename[:metadata_filename.rfind('.')]

            for source in region.sources:
                schedule_name = f"{region_name}-{source.name}"
                match source.spec:
                    case "gtfs":
                        schedule_file = f"{region_name}_{source.name}.gtfs.zip"

                        gtfs_feeds.append({
                            "id": schedule_name,
                            "path": schedule_file
                        })
                    case "gtfs-rt":
                        gtfsrt_feeds.append({
                            "id": schedule_name,
                            "url": source.url,
                            "authorization": source.authorization
                        })

    with open("motis/config.ini.j2") as f:
        template = Template(f.read())

        with open("out/config.ini", "w") as fo:
            fo.write(template.render(gtfs_feeds=gtfs_feeds,
                                     gtfsrt_feeds=gtfsrt_feeds,
                                     pbf_file=osm_map,
                                     flavour=flavour))
