#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import csv
import io
import transitland

from pathlib import Path
from metadata import *
from zipfile import ZipFile


if __name__ == "__main__":
    feed_dir = Path("feeds/")

    transitland_atlas = transitland.Atlas.load(Path("transitland-atlas/"))

    markdown = """
# Licenses of included feeds

"""

    attributions = []

    for feed in feed_dir.glob("*.json"):
        parsed = {}
        with open(feed, "r") as f:
            parsed = json.load(f)

        region = Region(parsed)
        for source in region.sources:
            if source.spec == "gtfs-rt":
                continue

            if (type(source) == TransitlandSource):
                source = transitland_atlas.source_by_id(source)
                if not source:
                    continue

            attribution = {}

            if source.license:
                if source.license.spdx_identifier:
                    attribution["spdx_identifier"] \
                        = source.license.spdx_identifier
                if source.license.url:
                    attribution["url"] = source.license.url

            attribution["copyright_holders"] = []

            metadata_filename = feed.name
            region_name = metadata_filename[:metadata_filename.rfind('.')]

            feed_path = Path(f"out/{region_name}_{source.name}.gtfs.zip")

            attribution["filename"] = feed_path.name
            markdown += "## Filename: " + feed_path.name + "  \r\n"

            if not feed_path.exists():
                print(f"Info: {feed_path} does not exist, skipping…")
                continue

            with ZipFile(feed_path) as z:
                with z.open("agency.txt", "r") as a:
                    with io.TextIOWrapper(a) as at:
                        agencyreader = \
                            csv.DictReader(at, delimiter=',', quotechar='"')
                        markdown += "### Copyright holders  \r\n"
                        for row in agencyreader:
                            attribution["copyright_holders"] \
                                .append(row["agency_name"])
                            markdown += " * " + row["agency_name"] + "  \r\n"

            attributions.append(attribution)

    with open("out/license.json", "w") as outfile:
        json.dump(attributions, outfile, indent=4, ensure_ascii=False)
    

    markdown += """
<!--
SPDX-FileCopyrightText: None
SPDX-License-Identifier: CC0-1.0
-->
"""
    with open("mkdocs-site/docs/licenses.md", "w") as outfile:
        outfile.write(markdown)
