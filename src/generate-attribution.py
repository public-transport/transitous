#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import csv
import io
import transitland

from pathlib import Path
from metadata import Source, TransitlandSource, Region
from zipfile import ZipFile
from typing import Optional


if __name__ == "__main__":
    feed_dir = Path("feeds/")

    transitland_atlas = transitland.Atlas.load(Path("transitland-atlas/"))

    attributions = []

    for feed in feed_dir.glob("*.json"):
        parsed = {}
        with open(feed, "r") as f:
            parsed = json.load(f)

        region = Region(parsed)
        for source in region.sources:
            if (type(source) == TransitlandSource):
                source = transitland_atlas.source_by_id(source)
                if not source:
                    continue

            if source.skip:
                continue

            if source.spec == "gtfs-rt":
                continue

            attribution: dict = {}

            if source.license:
                if source.license.spdx_identifier:
                    attribution["spdx_license_identifier"] \
                        = source.license.spdx_identifier
                if source.license.url:
                    attribution["license_url"] = source.license.url

            attribution["operators"] = []
            attribution["source"] = source.url

            metadata_filename = feed.name
            region_name = metadata_filename[:metadata_filename.rfind('.')]

            feed_path = Path(f"out/{region_name}_{source.name}.gtfs.zip")

            attribution["filename"] = feed_path.name

            if not feed_path.exists():
                print(f"Info: {feed_path} does not exist, skipping…")
                continue

            with ZipFile(feed_path) as z:
                with z.open("agency.txt", "r") as a:
                    with io.TextIOWrapper(a) as at:
                        agencyreader = \
                            csv.DictReader(at, delimiter=',', quotechar='"')
                        for row in agencyreader:
                            attribution["operators"] \
                                .append(row["agency_name"])

            attributions.append(attribution)

    with open("out/license.json", "w") as outfile:
        json.dump(attributions, outfile, indent=4, ensure_ascii=False)
