#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import urljoin

import requests


def index_existing() -> tuple[dict, set[str]]:
    existing = set()
    with Path("feeds/bg.json").open() as f:
        region = json.load(f)
        for source in region["sources"]:
            if "x-bgnap-subset-id" in source:
                existing.add(source["x-bgnap-subset-id"])

        return (region, existing)


def find_datasets(region: dict, existing: set[str]):
    datasets = requests.get("https://sipbg.gov.bg/bgnap/portal/api/catalog/datasets").json()

    for dataset in datasets:
        if not dataset["is_active"]:
            continue

        region_name = (
            dataset["regions"][0].lower().replace("national", "").replace(" ", "-").strip("-")
            if dataset["regions"]
            else ""
        )
        name = (
            dataset["name"]
            .lower()
            .replace(" ", "-")
            .replace("public-transport", "")
            .replace("transport-data", "")
            .replace("transport-scheme", "")
            .replace(region_name, "")
            .replace("passengers-transport", "")
            .replace("operator", "")
            .strip(" ")
            .strip("-")
        )

        name = f"{region_name}-{name}".strip("-")

        dataset_id = dataset["id"]

        subsets = requests.get(f"https://sipbg.gov.bg/bgnap/portal/api/catalog/datasets/{dataset_id}/subsets").json()

        for subset in subsets:
            subset_id = subset["id"]

            if subset_id in existing:
                continue

            match subset["format"]:
                case "gtfs-static":
                    files = requests.get(
                        f"https://sipbg.gov.bg/bgnap/portal/api/catalog/subsets/{subset_id}/files?format=gtfs-static"
                    ).json()
                    if not files:
                        continue

                    sources["sources"].append(
                        {
                            "name": name,
                            "type": "http",
                            "url": f"https://sipbg.gov.bg/bgnap/portal/api/catalog/subsets/{subset_id}/files?format=gtfs-static",
                            "function": "bgnap_latest_resource",
                            "x-bgnap-subset-id": subset_id,
                        }
                    )

                case "gtfs-realtime":
                    sources["sources"].append(
                        {
                            "name": name,
                            "type": "url",
                            "spec": "gtfs-rt",
                            "url": f"https://sipbg.gov.bg/bgnap/portal/api/catalog/subsets/{subset_id}/realtime-download",
                            "x-bgnap-type": subset["type"],
                            "x-bgnap-subset-id": subset_id,
                        }
                    )

    return sources


sources, existing = index_existing()
find_datasets(sources, existing)

with Path("feeds/bg.json").open("w") as f:
    json.dump(sources, fp=f, indent=4, ensure_ascii=False)
    f.write("\n")
