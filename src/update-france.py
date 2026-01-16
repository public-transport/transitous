#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
import json
import sys
from datetime import datetime, timedelta


if __name__ == "__main__":
    datasets = requests.get("https://transport.data.gouv.fr/api/datasets").json()

    region = json.load(open("feeds/fr.json", "r"))

    id_map = {}
    for feed in region["sources"]:
        # Don't handle feeds that are not from gouv.fr
        if "x-data-gov-fr-res-id" in feed:
            id_map[feed["x-data-gov-fr-res-id"]] = feed

    license_map = {
        "odc-odbl": "ODbL-1.0",
        "lov2": "etalab-2.0",
        "fr-lo": "etalab-2.0"
    }

    currently_active_ids = set()
    for dataset in datasets:
        for resource in dataset["resources"]:
            currently_active_ids.add(resource["id"])

        gtfs = list(
            filter(
                lambda r: "format" in r
                and (r["format"] == "GTFS" or r["format"] == "gtfs-rt"),
                dataset["resources"],
            )
        )
        gbfs = list(
            filter(
                lambda r: "format" in r
                and (r["format"] == "gbfs"),
                dataset["resources"],
            )
        )
        if gbfs and dataset["slug"]:
            # Exclude resources with "community_resource_publishers" field
            gbfs_resources = [
                r for r in gbfs if not r.get("community_resource_publisher")
            ]

            # Sort resources by the id field
            gbfs_resources.sort(key=lambda r: str(r.get("id", "")))

            if not gbfs_resources:
                print(f"{dataset['slug']} has no official GBFS data, or resources are removed.", file=sys.stderr)
                continue

            # Add all GBFS resources
            for resource in gbfs_resources:
                source_name = (
                    dataset["slug"]
                    if len(gbfs_resources) == 1
                    else dataset["slug"]
                    + "--"
                    + str(resource["id"])
                    .replace(" ", "-")
                    .replace("_", "-")
                    .replace("/", "-")
                )
                source = {
                    "type": "url",
                    "url": resource["url"],
                    "spec": "gbfs",
                    "license": {},
                    "x-data-gov-fr-res-id": resource["id"],
                    "x-data-gov-fr-res-title": resource["title"],
                    "managed-by-script": True
                }
                if "page_url" in dataset:
                    source["license"]["url"] = dataset["page_url"]
                if "licence" in dataset:
                    source["license"]["spdx-identifier"] = license_map.get(dataset["licence"])

                if resource["id"] in id_map:
                    id_map[resource["id"]].update(source)
                else:
                    source["name"] = source_name
                    region["sources"].append(source)

        if gtfs and dataset["slug"]:
            resources = list(
                filter(lambda r: "format" in r and r["format"] == "GTFS", gtfs)
            )
            # Exclude resources with "community_resource_publishers" field
            resources = [
                r for r in resources if not r.get("community_resource_publisher")
            ]

            # Sort resources by the id field
            resources.sort(key=lambda r: str(r.get("id", "")))

            if not resources:
                print(f"{dataset['slug']} only has GTFS-RT data?", file=sys.stderr)
                continue

            # Check if multiple GTFS feeds are present
            unique_GTFS = len(resources) == 1

            # Add all GTFS resources
            for resource in resources:
                source_name = (
                    dataset["slug"]
                    if unique_GTFS
                    else dataset["slug"]
                    + "--"
                    + str(resource["id"])
                    .replace(" ", "-")
                    .replace("_", "-")
                    .replace("/", "-")
                )

                source = {
                    "type": "http",
                    "url": resource["url"],
                    "fix": True,
                    "license": {},
                    "x-data-gov-fr-res-id": resource["id"],
                    "x-data-gov-fr-res-title": resource["title"],
                    "managed-by-script": True,
                }

                expired = "metadata" in resource and "end_date" and "end_date" in resource["metadata"] and resource["metadata"]["end_date"] and datetime.strptime(resource["metadata"]["end_date"], '%Y-%m-%d') < (datetime.now()-timedelta(days=0))
                if expired:
                    source["skip"] = True
                    source["skip-reason"] = "Feed is expired according to metadata"
                if "page_url" in dataset:
                    source["license"]["url"] = dataset["page_url"]
                if "licence" in dataset:
                    source["license"]["spdx-identifier"] = license_map.get(dataset["licence"])

                if resource["id"] in id_map:
                    id_map[resource["id"]].update(source)
                else:
                    source["name"] = source_name
                    region["sources"].append(source)

            def cond(r) -> bool:
                return (
                    "format" in r
                    and r["format"] == "gtfs-rt"
                    and "features" in r
                    and ("trip_updates" in r["features"] or "service_alerts" in r["features"] or len(r["features"]) == 0)
                )

            def contains_name(out, name_to_check):
                return any(entry.get("name") == name_to_check and not entry.get("skip") for entry in out)

            resources = list(filter(cond, gtfs))
            resources.sort(key=lambda r: str(r.get("id", "")))
            if not resources:
                continue

            for resource in resources:
                # We can only continue if their is a unique GTFS file, or if there is a `gtfs_rt_select` entry for this dataset
                feed_name = dataset["slug"]

                # Check if there is a corresponding GTFS feed with the same name!
                source = {
                    "type": "url",
                    "url": resource["url"],
                    "x-data-gov-fr-res-title": resource["title"],
                    "license": {},
                }
                if "page_url" in dataset:
                    source["license"]["url"] = dataset["page_url"]

                if "licence" in dataset:
                    source["license"]["spdx-identifier"] = license_map.get(dataset["licence"])

                source["spec"] = "gtfs-rt"
                source["x-data-gov-fr-res-id"] = resource["id"]
                source["managed-by-script"] = True

                if resource["id"] in id_map:
                    id_map[resource["id"]].update(source)
                else:
                    if not contains_name(region["sources"], feed_name):
                        print(
                            f"Warning: {feed_name} GTFS-RT needs to match the name of its static GTFS feed! This needs manual editing to work",
                            file=sys.stderr,
                        )

                    source["name"] = source_name
                    source["skip"] = True
                    source["skip-reason"] = "Needs to be renamed to match the corresponding static feed"

                    region["sources"].append(source)

    # Remove no longer existing entries
    region["sources"] = list(filter(lambda feed: "x-data-gov-fr-res-id" not in feed or feed["x-data-gov-fr-res-id"] in currently_active_ids, region["sources"]))

    with open("feeds/fr.json", "w") as f:
        json.dump(region, f, indent=4, ensure_ascii=False)
        f.write("\n")
