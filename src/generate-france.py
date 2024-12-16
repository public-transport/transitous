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

    remove_title = [
        "Lien vers le GTFS du r\u00e9seau urbain de Parthenay (PYBUS)",  # Duplicate data
        "GTFS SANPROVENCE Ulysse (Navette Mille Sabords inclus) ",  # Duplicate data
        "GTFS CG13 Cartreize",  # Duplicate data
        "GTFS Libébus",  # Duplicate data
        "GTFS Les bus de la Côte Bleue",  # Duplicate data
        "GTFS CIOTABUS",  # Duplicate data
        "GTFS  Les bus de la Marcouline",  # Duplicate data
        "GTFS CPA",  # Duplicate data
        "GTFS AIXENBUS ",  # Duplicate data
        "GTFS RTM",  # Duplicate data
        "GTFS Agglobus - Les lignes de l'agglo",  # Duplicate data
        "GTFS Frioul if express",  # Duplicate data
        "GTFS Bus des collines",  # Duplicate data
        "GTFS Les bus des Cigales",  # Duplicate data
        "GTFS Les bus de l'étang",  # Duplicate data
        "Transaltitude (38) - Offre théorique au format GTFS",  # Remove almost useless additional feed, + easier GTFS-RT matching
        "gtfs-t2c_plus_scolaire.zip",  # Remove additional school feed, + easier GTFS-RT matching
        "Réseau Sankéo - Lignes Scolaires",  # Remove additional school feed, + easier GTFS-RT matching
        "GTFS - Horaires théoriques + TAD + Scolaire + Shapes",  # Remove additional DRT + school feed, + easier GTFS-RT matching
        "gtfs-navineo.zip",  # Remove old data, + easier GTFS-RT matching
        "Description du TAD zonal (GTFS-Flex) - réseau Corolis",  # Remove additional DRT feed, + easier GTFS-RT matching
        "Description du TAD zonal (GTFS-Flex) - réseau AXO",  # Remove additional DRT feed, + easier GTFS-RT matching
        "Description du TAD zonal (GTFS-Flex) - réseau Sablons Bus",  # Remove additional DRT feed, + easier GTFS-RT matching
        "Description du TAD zonal (GTFS-Flex) - réseau Le Bus",  # Remove additional DRT feed, + easier GTFS-RT matching
    ]

    # Map for each slug, if needed, the selected GTFS-RT feeds to the corresponding GTFS title
    gtfs_rt_select = {
        "moca-communaute-de-communes-caux-austreberthe": {
            "Données gobales en temps réel du réseau MOCA": "pt-th-offer-moca-gtfs-20240529-816-opendata.zip",
        },
        "breizhgo-car": {
            "Breizhgo Car 35": "Breizhgo-35",
            "Breizhgo Car - Rennes – Loudéac/Pontivy": "Breizhgo-Car---Rennes-–-Loudéac-Pontivy",
            "Breizhgo Car 22": "Breizhgo-Car-22",
        },
        "versions-des-horaires-theoriques-des-lignes-de-bus-et-de-metro-du-reseau-star-au-format-gtfs": {
            "https://proxy.transport.data.gouv.fr/resource/star-rennes-integration-gtfs-rt-trip-update": "ID82587",
        },
        "horaires-theoriques-et-en-temps-reel-des-bus-et-autocars-circulant-sur-le-reseau-cap-cotentin": {
            "Horaires en temps réel des lignes régulières du réseau Cap Cotentin": "Horaires-théoriques-des-lignes-régulières-et-secondaires-du-réseau-Cap-Cotentin"
        },
    }

    naming_exceptions = [
        "versions-des-horaires-theoriques-des-lignes-de-bus-et-de-metro-du-reseau-star-au-format-gtfs"
    ]

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
            resources = [r for r in resources if r.get("title") not in remove_title]

            # Sort resources alphabetically by the title field
            resources.sort(key=lambda r: r.get("title", "").lower())

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
                    else (
                        dataset["slug"] + "--ID" + str(resource["id"]).replace(" ", "-").replace("_", "-").replace("/", "-")
                        if dataset["slug"] in naming_exceptions
                        else dataset["slug"] + "--" + resource["title"].replace(" ", "-").replace("_", "-").replace("/", "-")
                    )
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

            resources = list(filter(cond, gtfs))
            resources.sort(key=lambda r: r.get("title", "").lower())
            if not resources:
                continue
            elif len(resources) == 1:
                source = {}
                if unique_GTFS:
                    source["name"] = dataset["slug"]
                else:
                    match = gtfs_rt_select.get(dataset["slug"])
                    if match and resources[0]["title"] in match:
                        source["name"] = (
                            dataset["slug"] + "--" + match.get(resources[0]["title"])
                        )
                    else:
                        print(
                            f"Warning: {dataset['slug']} GTFS-RT mismatch possible?",
                            file=sys.stderr,
                        )
                        continue
                source["type"] = "url"
                source["url"] = resources[0]["original_url"]
                if dataset["slug"] in skip:
                    source["skip"] = True
                if "page_url" in dataset:
                    source["license"] = {"url": dataset["page_url"]}
                source["spec"] = "gtfs-rt"
                out.append(source)
            elif len(resources) > 1:
                matches = gtfs_rt_select.get(dataset["slug"])
                if matches:
                    for resource in resources:
                        if resource["title"] in matches:
                            source = {}
                            source["name"] = (
                                dataset["slug"]
                                if unique_GTFS
                                else dataset["slug"]
                                + "--"
                                + matches.get(resource["title"])
                            )
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
                                f"{dataset['slug']} has skipped {resource["title"]} GTFS-RT feed because not selected!",
                                file=sys.stderr,
                            )

                else:
                    print(
                        f"{dataset['slug']} has multiple unmatched GTFS-RT feeds?",
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
