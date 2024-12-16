#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
import json
import sys


if __name__ == "__main__":
    datasets = requests.get("https://transport.data.gouv.fr/api/datasets").json()

    skip = [
        "blablacar-bus-horaires-theoriques-et-temps-reel-du-reseau-europeen",  # Already in eu.json
        "flixbus-horaires-theoriques-du-reseau-europeen-1",  # Already in eu.json
        "gtfs-static-et-real-time-transporteur-thalys",  # Already in eu.json
        "eurostar-gtfs",  # Already in eu.json
        "arrets-horaires-et-parcours-theoriques-du-reseau-routier-regional-de-transport-scolaire-et-interurbain-60-oise",  # broken
        "horaires-theoriques-des-cars-du-rhone",  # requires authentication
        "horaires-theoriques-des-lignes-scolaires-du-reseau-transports-en-commun-lyonnais",  # requires authentication
        "horaires-theoriques-du-reseau-libellule-sytral-de-la-communaute-dagglomeration-de-villefranche-beaujolais-saone",  # requires authentication
        "horaires-theoriques-du-reseau-transports-en-commun-lyonnais",
        "description-de-loffre-tad-tao-gtfs-flex-orleans-metropole",
        "reseau-de-bus-urbain-horizon",  # 404 not found
        "horaires-theoriques-et-temps-reel-de-la-navette-du-pont-de-saint-nazaire-gtfs-gtfs-rt",
        "horaires-theoriques-de-la-navette-velo-du-pont-de-saint-nazaire-gtfs",  # no agency.txt
        "horaires-theoriques-et-temps-reel-des-navettes-de-la-ligne-bagneres-la-mongie-gtfs-gtfs-rt",  # 404 not found
        "horaires-theoriques-et-temps-reel-des-navettes-de-la-station-de-tignes-gtfs-gtfs-rt",
        "horaires-theoriques-et-temps-reel-des-navettes-de-val-disere-gtfs-gtfs-rt",  # 404 not found
        "horaires-theoriques-et-temps-reel-des-navettes-hivernales-de-lalpe-dhuez-gtfs-gtfs-rt",  # 404 not found
        "arrets-horaires-et-parcours-theoriques-des-bus-du-reseau-des-transports-publics-envibus",  # timeout
        "horaires-theoriques-du-service-rhonexpress-de-la-metropole-de-lyon-et-du-departement-du-rhone",  # 401 not authorized
        "3cm-horaires-theoriques-du-reseau-de-transport-urbain-solutions-transport-3cm",  # Confuses MOTIS and doesn't contain any trips
        "donnees-theoriques-et-temps-reel-du-reseau-corolis-interurbain-communaute-dagglomeration-du-beauvaisis",  # Confuses MOTIS
        "donnees-theoriques-et-temps-reel-du-reseau-axo-communaute-dagglomeration-creil-sud-oise",  # Confuses MOTIS
        "arrets-horaires-et-parcours-theoriques-gtfs-du-reseau-routier-regional-de-transport-scolaire-62-pas-de-calais",  # agency.txt
        "arrets-horaires-et-parcours-theoriques-gtfs-du-reseau-routier-regional-de-transport-interurbain-62-pas-de-calais",  # agency.txt
        "naolib-arrets-horaires-et-circuits",  # Incomplete read
        "offre-transport-du-reseau-txik-txak-nord-ex-chronoplus-gtfs",  # 404
        "horaires-theoriques-et-temps-reel-lignes-scolaires-sankeo-perpignan-gtfs-gtfs-rt",  # 404
        "reseau-de-transport-en-commun-transagglo-de-dlva",  # Resource not available
        "donnees-theoriques-et-temps-reel-du-reseau-corolis-urbain-communaute-dagglomeration-du-beauvaisis",  # agency.txt
        "donnees-theoriques-et-temps-reel-du-reseau-tic-interurbain-communaute-dagglomeration-de-la-region-de-compiegne-et-de-la-basse-automne",  # agency.txt
        "donnees-theoriques-et-temps-reel-du-reseau-tic-urbain-communaute-dagglomeration-de-la-region-de-compiegne-et-de-la-basse-automne",  # agency.txt
        "arrets-horaires-et-circuit-de-la-lignes-yeu-continent-gtfs",  # agency.txt
        "caen-la-mer-reseau-twisto-gtfs-siri",  # Temporary removal, 401 error
    ]

    # List of individual resource ids (located in datasets) we want to remove
    remove_resources = [
        # "Lien vers le GTFS du r\u00e9seau urbain de Parthenay (PYBUS)",  # Duplicate data
        "82619",
        # "GTFS SANPROVENCE Ulysse (Navette Mille Sabords inclus) ",  # Duplicate data
        "39591",
        # "GTFS CG13 Cartreize",  # Duplicate data
        "39602",
        "GTFS Libébus",  # Duplicate data
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
    ]

    # Map for each dataset slug, if needed, the selected GTFS-RT id to the corresponding GTFS id
    gtfs_rt_select = {
        "moca-communaute-de-communes-caux-austreberthe": {
            "82630": "82309",
        },
        "breizhgo-car": {
            "81804": "81463",
            "81805": "81466",
            "81806": "81461",
        },
        "versions-des-horaires-theoriques-des-lignes-de-bus-et-de-metro-du-reseau-star-au-format-gtfs": {
            "82161": "82587",
        },
        "horaires-theoriques-et-en-temps-reel-des-bus-et-autocars-circulant-sur-le-reseau-cap-cotentin": {
            "79830": "79831"
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
        if gtfs:
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
                    "url": resource["original_url"],
                    "fix": True,
                }
                if dataset["slug"] in skip:
                    source["skip"] = True
                if "page_url" in dataset:
                    source["license"] = {}
                    source["license"]["url"] = dataset["page_url"]
                out.append(source)

            def cond(r) -> bool:
                return (
                    "format" in r
                    and r["format"] == "gtfs-rt"
                    and "features" in r
                    and "trip_updates" in r["features"]
                )

            def contains_name(out, name_to_check):
                return any(entry.get("name") == name_to_check for entry in out)

            resources = list(filter(cond, gtfs))
            resources.sort(key=lambda r: str(r.get("id", "")))
            if not resources:
                continue
            matches = gtfs_rt_select.get(dataset["slug"])
            # We can only continue if their is a unique GTFS file, or a if there is a `gtfs_rt_select` entry for this dataset
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
                                f"{dataset['slug']} has skipped {resource["title"]} GTFS-RT feed because not selected!",
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
                        if "page_url" in dataset:
                            source["license"] = {"url": dataset["page_url"]}
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

    # This is an aggregated and improved feed that we want to keep
    out.append(
        {
            "name": "Brittany",
            "type": "transitland-atlas",
            "transitland-atlas-id": "f-gbwc-mobibreizh",
            "fix": True,
        }
    )

    with open("feeds/fr.json", "r") as f:
        region = json.load(f)

    region["sources"] = out

    with open("feeds/fr.json", "w") as f:
        json.dump(region, f, indent=4, ensure_ascii=False)
