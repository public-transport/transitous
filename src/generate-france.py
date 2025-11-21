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

    # List of datasets to skip
    skip = [
        "blablacar-bus-horaires-theoriques-et-temps-reel-du-reseau-europeen",  # Already in eu.json
        "flixbus-horaires-theoriques-du-reseau-europeen-1",  # Already in eu.json
        "horaires-theoriques-des-cars-du-rhone",  # requires authentication
        "horaires-theoriques-des-lignes-scolaires-du-reseau-transports-en-commun-lyonnais",  # requires authentication
        "horaires-theoriques-du-reseau-libellule-sytral-de-la-communaute-dagglomeration-de-villefranche-beaujolais-saone",  # requires authentication
        "horaires-theoriques-de-la-navette-velo-du-pont-de-saint-nazaire-gtfs",  # Could not check validity, because the time zone could not be detected
        "arrets-horaires-et-parcours-theoriques-des-bus-du-reseau-des-transports-publics-envibus",  # timeout
        "horaires-theoriques-du-service-rhonexpress-de-la-metropole-de-lyon-et-du-departement-du-rhone",  # 401 not authorized
        "horaires-theoriques-et-temps-reel-des-navettes-de-la-station-de-tignes-gtfs-gtfs-rt", # 500
        "tico-bus-horaires-theoriques-du-reseau-de-transport-urbain-tico", # name or service not known
        "caen-la-mer-reseau-twisto-gtfs-siri", # 404, incompatible
        "reseau-de-bus-urbain-horizon", # name or service not known
        "gtfs-et-gtfs-rt-reseau-orizo-grand-avignon", # name or service not known
        "offre-de-transport-du-reseau-fluo-grand-est-moselle-57",
        "navettes-bourg-saint-maurice",
        "horaires-theoriques-et-en-temps-reel-de-la-navette-velo-du-pont-de-saint-nazaire-gtfs-gtfs-rt-2023", # unknown timezone
        "horaires-theoriques-et-temps-reel-des-navettes-hivernales-de-lalpe-dhuez-gtfs-gtfs-rt",
        "reseau-de-transports-collectifs-de-la-ccgq", # expired
        "reseau-de-transport-interurbain-mobigo-en-bourgogne-franche-comte", # connection timeout
    ]

    # Map of datasets to MOTIS Lua scripts to apply to them
    scripts = {
        "eurostar-gtfs-plan-de-transport-et-temps-reel": "fr-eurostar.lua",
        "arrets-itineraires-et-horaires-theoriques-des-reseaux-de-transport-des-membres-de-jvmalin": "fr-jvmalin.lua"
    }

    # List of datasets to remove
    remove = [
        "tier-dott-gbfs-france", # Duplicate dataset (use local ones)
        "tier-dott-gbfs-saint-quentin-en-yvelines", # Deprecated dataset
        "horaires-des-tgv", # replaced by horaires-sncf
        "horaires-des-lignes-intercites-sncf", # replaced by horaires-sncf
        "horaires-des-lignes-ter-sncf" # replaced by horaires-sncf
    ]

    # List of individual resource ids (located in datasets) we want to remove
    remove_resources = [
        # "GTFS SANPROVENCE Ulysse (Navette Mille Sabords inclus) ",  # Duplicate data
        "39591",
        # "GTFS CG13 Cartreize",  # Duplicate data
        "39602",
        # "GTFS Libébus",  # Duplicate data
        "39592",
        # "GTFS Les bus de la Côte Bleue",  # Duplicate data
        "39596",
        # "GTFS CIOTABUS",  # Duplicate data
        "80736",
        # "GTFS  Les bus de la Marcouline",  # Duplicate data
        "39595",
        # "GTFS CPA",  # Duplicate data
        "39601",
        # "GTFS AIXENBUS ",  # Duplicate data
        "39603",
        # "GTFS RTM",  # Duplicate data
        "39589",
        # "GTFS Agglobus - Les lignes de l'agglo",  # Duplicate data
        "39598",
        # "GTFS Frioul if express",  # Duplicate data
        "39599",
        # "GTFS Bus des collines",  # Duplicate data
        "39593",
        # "GTFS Les bus des Cigales",  # Duplicate data
        "39594",
        # "GTFS Les bus de l'étang",  # Duplicate data
        "39597",
        # "Transaltitude (38) - Offre théorique au format GTFS",  # Remove almost useless additional feed, + easier GTFS-RT matching
        "82299",
        # "gtfs-t2c_plus_scolaire.zip",  # Remove additional school feed, + easier GTFS-RT matching
        "82302",
        # "Réseau Sankéo - Lignes Scolaires",  # Remove additional school feed, + easier GTFS-RT matching
        "82271",
        # "GTFS - Horaires théoriques + TAD + Scolaire + Shapes",  # (ametis), Remove additional DRT + school feed, + easier GTFS-RT matching
        "80223",
        # "gtfs-navineo.zip"  # (tcat-troyes), Remove old data, + easier GTFS-RT matching
        "79847",
        # "Description du TAD zonal (GTFS-Flex) - réseau Corolis",  # Remove additional DRT feed, + easier GTFS-RT matching
        "81650",
        # "Description du TAD zonal (GTFS-Flex) - réseau AXO",  # Remove additional DRT feed, + easier GTFS-RT matching
        "81645",
        # "Description du TAD zonal (GTFS-Flex) - réseau Sablons Bus",  # Remove additional DRT feed, + easier GTFS-RT matching
        "81651",
        # "Description du TAD zonal (GTFS-Flex) - réseau Le Bus",  # Remove additional DRT feed, + easier GTFS-RT matching
        "81652",
        # Very invalid calendar_dates.txt
        "81648", "81649",
        # Remove old unavailable feed
        "81906",
        # Unavailable
        "82306",
        # Remove invalid duplicates
        "80484", "80485",
        # Remove duplicate
        "82695",
        # Remove invalid duplicates
        "63612", "63613", "63614",
        # Unavailable
        "83019",
        # old/duplicate data
        "81899", "83193", "82168",
        # Azalys, Blois : empty GTFS files
        "83425", "83426"
    ]

    # Map for each dataset slug, if needed, the selected GTFS-RT id to the corresponding GTFS id
    gtfs_rt_select = {
         "versions-des-horaires-theoriques-des-lignes-de-bus-et-de-metro-du-reseau-star-au-format-gtfs": {
            "82161": "83281",
            "82162": "83281",
            "82163": "83281"
        },
        "breizhgo-car": {
            "81804": "81463",
            "81805": "81466",
            "81806": "81461",
        },
        "horaires-theoriques-et-en-temps-reel-des-bus-et-autocars-circulant-sur-le-reseau-cap-cotentin": {
            "79830": "79831"
        },
        "gtfs-move-vendome": {
            "80381": "82832"
        },
        "gtfs-sankeo": {
            "82901": "82900",
            "82273": "82902"
        },
        "moca-communaute-de-communes-caux-austreberthe": {
            "82633": "82309",
            "82631": "82309",
        },
    }

    out: list[dict] = []
    for dataset in datasets:
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
        if gbfs and (dataset["slug"] not in remove):
            # Exclude resources with "community_resource_publishers" field
            gbfs_resources = [
                r for r in gbfs if not r.get("community_resource_publisher")
            ]

            # Remove resources with title in remove_title
            gbfs_resources = [
                r for r in gbfs_resources if str(r.get("id")) not in remove_resources
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
                    "name": source_name,
                    "type": "url",
                    "url": resource["original_url"],
                    "spec": "gbfs",
                    "license": {},
                }
                if dataset["slug"] in skip:
                    source["skip"] = True
                if "page_url" in dataset:
                    source["license"]["url"] = dataset["page_url"]
                if dataset["licence"] == "odc-odbl":
                    source["license"]["spdx-identifier"] = "ODbL-1.0"
                if dataset["licence"] in ["lov2", "fr-lo"]:
                    source["license"]["spdx-identifier"] = "etalab-2.0"
                out.append(source)
        if gtfs and (dataset["slug"] not in remove):
            resources = list(
                filter(lambda r: "format" in r and r["format"] == "GTFS", gtfs)
            )
            # Exclude resources with "community_resource_publishers" field
            resources = [
                r for r in resources if not r.get("community_resource_publisher")
            ]

            # Remove resources with title in remove_title
            resources = [
                r for r in resources if str(r.get("id")) not in remove_resources
            ]

            # Sort resources by the id field
            resources.sort(key=lambda r: str(r.get("id", "")))

            if not resources:
                print(f"{dataset['slug']} only has GTFS-RT data?", file=sys.stderr)
                continue

            # Check if multiple GTFS feeds are present
            unique_GTFS = True
            if len(resources) > 1:
                unique_GTFS = False

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
                    "name": source_name,
                    "type": "http",
                    "url": resource["url"],
                    "url-override": resource["original_url"],
                    "fix": True,
                    "license": {},
                }
                if dataset["slug"] in skip:
                    source["skip"] = True
                expired = "metadata" in resource and "end_date" and "end_date" in resource["metadata"] and resource["metadata"]["end_date"] is not None and datetime.strptime(resource["metadata"]["end_date"], '%Y-%m-%d') < (datetime.now()-timedelta(days=3))
                if expired:
                    print("Feed expired according to metadata, setting to skip=True:", resource["metadata"]["end_date"], feed_name)
                    source["skip"] = True
                if "page_url" in dataset:
                    source["license"]["url"] = dataset["page_url"]
                if dataset["licence"] == "odc-odbl":
                    source["license"]["spdx-identifier"] = "ODbL-1.0"
                if dataset["licence"] in ["lov2", "fr-lo"]:
                    source["license"]["spdx-identifier"] = "etalab-2.0"
                if dataset["slug"] in scripts:
                    source["script"] = scripts[dataset["slug"]]
                out.append(source)

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
            matches = gtfs_rt_select.get(dataset["slug"])
            # We can only continue if their is a unique GTFS file, or if there is a `gtfs_rt_select` entry for this dataset
            if matches or unique_GTFS:
                for resource in resources:
                    if matches:
                        if str(resource["id"]) in matches:
                            if unique_GTFS:
                                feed_name = dataset["slug"]
                            else:
                                feed_name = (
                                    dataset["slug"]
                                    + "--"
                                    + matches.get(str(resource["id"]))
                                )
                        else:
                            print(
                                f"{dataset['slug']} has skipped {resource['title']} GTFS-RT feed because not selected!",
                                file=sys.stderr,
                            )
                            continue
                    # If not matches, then it must be the unique_GTFS case
                    else:
                        feed_name = dataset["slug"]

                    # Check if there is a corresponding GTFS feed with the same name!
                    if contains_name(out, feed_name):
                        source = {}
                        source["name"] = feed_name
                        source["type"] = "url"
                        source["url"] = resource["original_url"]
                        if dataset["slug"] in skip:
                            source["skip"] = True
                        source["license"] = {}
                        if "page_url" in dataset:
                            source["license"]["url"] = dataset["page_url"]
                        if dataset["licence"] == "odc-odbl":
                            source["license"]["spdx-identifier"] = "ODbL-1.0"
                        if dataset["licence"] in ["lov2", "fr-lo"]:
                            source["license"]["spdx-identifier"] = "etalab-2.0"
                        source["spec"] = "gtfs-rt"
                        out.append(source)
                    else:
                        print(
                            f"Warning: {feed_name} GTFS-RT needs to match the name of its static GTFS feed!",
                            file=sys.stderr,
                        )
            else:
                print(
                    f"{dataset['slug']} has unmatched GTFS-RT feed(s)?",
                    file=sys.stderr,
                )
                continue

    # TCL(Lyon) unofficial feed + suburban buses
    out.extend([
        {
            "name": "lyon-tcl",
            "type": "http",
            "url": "https://gtfs.bus-tracker.fr/tcl.zip",
            "license": {
                "spdx-identifier": "ODbL-1.0"
            }
        },
        {
            "name": "lyon-tcl",
            "type": "url",
            "url": "https://gtfs.bus-tracker.fr/gtfs-rt/tcl",
            "license": {
                "spdx-identifier": "ODbL-1.0"
            },
            "spec": "gtfs-rt"
        },
        {
            "name": "transports-faure-28bi",
            "type": "http",
            "url": "https://pysae.com/api/v2/groups/transports-faure-28bi/gtfs/pub",
            "license": {
                "spdx-identifier": "ODbL-1.0"
            }
        },
        {
            "name": "transports-faure-28bi",
            "type": "url",
            "url": "https://pysae.com/api/v2/groups/transports-faure-28bi/gtfs-rt",
            "license": {
                "spdx-identifier": "ODbL-1.0"
            },
            "spec": "gtfs-rt"
        },
        {
            "name": "cars-faure-tcl",
            "type": "http",
            "url": "https://pysae.com/api/v2/groups/cars-faure-tcl/gtfs/pub",
            "license": {
                "spdx-identifier": "ODbL-1.0"
            }
        },
        {
            "name": "cars-faure-tcl",
            "type": "url",
            "url": "https://pysae.com/api/v2/groups/cars-faure-tcl/gtfs-rt",
            "license": {
                "spdx-identifier": "ODbL-1.0"
            },
            "spec": "gtfs-rt"
        },
    ])
    # official feeds without available zip files at data.gouv.fr for some reason
    out.append(
        {
            "name": "caen-la-mer-reseau-twisto-gtfs-siri",
            "type": "http",
            "url": "https://data.twisto.fr/api/explore/v2.1/catalog/datasets/fichier-gtfs-du-reseau-twisto/alternative_exports/gtfs_twisto_zip/",
            "license": {
                "url": "https://data.twisto.fr/explore/dataset/fichier-gtfs-du-reseau-twisto/information/",
                "spdx-identifier": "ODbL-1.0"
            }
        }
    )

    
    with open("feeds/fr.json", "r") as f:
        region = json.load(f)

    region["sources"] = out

    with open("feeds/fr.json", "w") as f:
        json.dump(region, f, indent=4, ensure_ascii=False)
