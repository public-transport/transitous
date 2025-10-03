#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
import json

TIMETABLE_YEARS = [2025]


def remove_duplicate_dashes(text: str) -> str:
    out = []

    prev = None
    for c in text:
        if c == "-" and prev == "-":
            prev = c
            continue

        prev = c
        out.append(c)

    return "".join(out)


def add_feed(year: int) -> dict:
    url = f"https://data.mobilitaetsverbuende.at/api/public/v1/data-sets/{set_id}/{year}/file"
    return {
        "name": remove_duplicate_dashes(
            data_set["nameEn"]
            .replace("Timetable Data", "")
            .replace("(GTFS)", "")
            .strip()
            .replace(" ", "-")) + "-" + str(year),
        "type": "http",
        "url": url,
        "license": {"url": data_set["termsOfUseUrlEn"]},
        "fix": True,
        "function": "mvo_keycloak_token",
        "http-options": {
            "fetch-interval-days": 2
        }
    }


if __name__ == "__main__":
    ignore = [
        "70",  # Same data but outdated
        "72",  # contains multiple zip files, not what we need
    ]
    scripts = {
        "53": "at.lua", # Styria
        "54": "at.lua", # Salzbug
        "56": "at.lua", # Upper Austria
        "66": "at.lua", # ÖBB
    }

    data_sets = requests.get(
        "https://data.mobilitaetsverbuende.at/api/public/v1/data-sets?tagIds=20&tagFilterModeInclusive=false"
    ).json()

    sources: list[dict] = []

    for data_set in data_sets:
        set_id = data_set["id"]
        if set_id in ignore:
            continue

        if "Flex" in data_set["nameEn"]:
            continue

        for year in TIMETABLE_YEARS:
            source = add_feed(year)
            if set_id == "66":  # ÖBB
                source["display-name-options"] = {}
                source["display-name-options"]["copy-trip-names-matching"] = \
                    r"((IC)|(ECB)|(EC)|(RJ)|(RJX)|(D)|(NJ)|(EN)|(CJX)|(ICE)|(IR)|(REX)|(R)|(ER)|(ATB)|(WB)) \d+"
                source["display-name-options"]["keep-route-names-matching"] = \
                    r"((RE)|(RB)|S) ?\d+"
            if set_id in scripts:
                source["script"] = scripts[set_id]
            sources.append(source)

    region = {}

    with open("feeds/at.json", "r") as f:
        region = json.load(f)

    region["sources"] = sources

    with open("feeds/at.json", "w") as f:
        json.dump(region, fp=f, indent=4, ensure_ascii=False)
        f.write("\n")
