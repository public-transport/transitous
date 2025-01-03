#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import csv
import io
import transitland
import pycountry

from pathlib import Path
from metadata import TransitlandSource, Region, UrlSource, HttpSource
from zipfile import ZipFile
from typing import Optional


REGIONS = {"EU": "European Union"}


def filter_duplicates(elems):
    prev = None
    out = []
    for elem in elems:
        if prev == elem:
            continue
        prev = elem
        out.append(elem)

    return out


def http_source_attribution(source: HttpSource) -> Optional[dict]:
    attribution: dict = {}

    if source.license:
        if source.license.spdx_identifier:
            attribution["spdx_license_identifier"] = \
                source.license.spdx_identifier
        if source.license.url:
            attribution["license_url"] = source.license.url

    attribution["operators"] = []
    attribution["source"] = source.url

    feed_path = Path(f"out/{source_id}.gtfs.zip")
    attribution["filename"] = feed_path.name

    human_name: str = (
        feed_path.name.replace(".gtfs.zip", "").split("_")[1].replace("-", " ")
    )
    human_name = " ".join(
        map(lambda w: w[0].upper() + w[1:] if len(w) > 0 else w, human_name.split(" "))
    )
    attribution["human_name"] = human_name

    if not feed_path.exists():
        print(f"Info: {feed_path} does not exist, skipping…")
        return None

    contacts: list[dict] = []

    with ZipFile(feed_path) as z:
        if "feed_info.txt" in z.namelist():
            with z.open("feed_info.txt", "r") as i:
                with io.TextIOWrapper(i) as it:
                    inforeader = csv.DictReader(it, delimiter=",", quotechar='"')
                    publisher = next(inforeader)
                    attribution["publisher"] = {}
                    attribution["publisher"]["name"] = publisher["feed_publisher_name"]
                    attribution["publisher"]["url"] = publisher["feed_publisher_url"]

                    contact = {
                            "type": "publisher",
                            "name": publisher["feed_publisher_name"],
                            "email": publisher.get("feed_contact_email"),
                            "url": publisher.get("feed_contact_url")
                    }

                    contacts.append(contact)

        with z.open("agency.txt", "r") as a:
            with io.TextIOWrapper(a) as at:
                agencyreader = list(csv.DictReader(at, delimiter=",", quotechar='"'))

                attribution["operators"] = \
                    filter_duplicates(map(lambda agency: agency["agency_name"],
                                          agencyreader))

                contacts += map(lambda agency: {
                        "type": "agency",
                        "agency_id": agency.get("agency_id"),
                        "name": agency["agency_name"],
                        "email": agency.get("agency_email")
                    }, agencyreader)

        if "attributions.txt" in z.namelist():
            with z.open("attributions.txt", "r") as a:
                with io.TextIOWrapper(a) as at:
                    attributionstxt = csv.DictReader(at, delimiter=",", quotechar='"')
                    attribution["attributions"] = filter_duplicates(
                        map(
                            lambda contrib: {
                                "name": contrib["organization_name"],
                                "url": contrib.get("attribution_url")
                            },
                            attributionstxt,
                        )
                    )

                    attribution_contacts = map(lambda operator: {
                            "type": "attribution",
                            "name": operator["organization_name"],
                            "email": operator.get("attribution_email")
                        }, attributionstxt)

                    contacts += attribution_contacts

    attribution["contacts"] = \
        list(filter(lambda c: c.get("email") or c.get("url"),
                    contacts))

    if (
        "operators" in attribution
        and len(attribution["operators"]) == 1
        and len(attribution["operators"][0]) > 1
    ):
        attribution["human_name"] = attribution["operators"][0]

    attribution["region_code"] = region_code
    attribution["region_name"] = region_name

    return attribution


def rt_attribution(source: UrlSource) -> dict:
    attribution = {}
    if source.license:
        if source.license.spdx_identifier:
            attribution[
                "rt_spdx_license_identifier"
            ] = source.license.spdx_identifier
        if source.license.url:
            attribution["rt_license_url"] = \
                source.license.url
    attribution["rt_source"] = source.url

    return attribution




if __name__ == "__main__":
    feed_dir = Path("feeds/")

    transitland_atlas = transitland.Atlas.load(Path("transitland-atlas/"))

    attributions: dict[str, dict] = {}

    for feed in sorted(feed_dir.glob("*.json")):
        parsed = {}
        with open(feed, "r") as f:
            parsed = json.load(f)

        metadata_filename = feed.name
        region_code_lower = metadata_filename[: metadata_filename.rfind(".")]
        region_code = region_code_lower.upper()
        region_name = ""
        subdivision = pycountry.subdivisions.get(code=region_code)
        if not subdivision:
            country = pycountry.countries.get(alpha_2=region_code)
            if country:
                region_name = country.name
            else:
                region_name = REGIONS[region_code]
        else:
            region_name = subdivision.name

        region = Region(parsed)
        for source in region.sources:
            source_id = f"{region_code_lower}_{source.name}"

            if source is TransitlandSource:
                source = transitland_atlas.source_by_id(source)
                if not source:
                    continue

            if source.skip:
                continue

            match source:
                case UrlSource() if source.spec == "gtfs-rt":
                    attribution = rt_attribution(source)

                    if source_id not in attributions:
                        attributions[source_id] = attribution
                    else:
                        attributions[source_id] |= attribution
                case HttpSource():
                    http_attribution = http_source_attribution(source)
                    if not http_attribution:
                        continue

                    if source_id not in attributions:
                        attributions[source_id] = http_attribution
                    else:
                        print("Warning: Found duplicate source name:", source_id)
                        attributions[source_id] |= http_attribution

    with open("out/license.json", "w") as outfile:
        json.dump(
            [item for id, item in sorted(attributions.items())],
            outfile,
            indent=4,
            ensure_ascii=False,
        )
