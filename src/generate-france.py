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
        "horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs-jeux-olympiques-et-paralympiques-de-paris-2024-datahub",  # try removing
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
        "breizhgo-bateaux",  # Confuses MOTIS and doesn't contain any trips
        "donnees-theoriques-et-temps-reel-du-reseau-pass-thelle-bus-communaute-de-communes-thelloise",  # Confuses MOTIS and doesn't contain any trips
        "3cm-horaires-theoriques-du-reseau-de-transport-urbain-solutions-transport-3cm",  # Confuses MOTIS and doesn't contain any trips
        "donnees-theoriques-et-temps-reel-du-reseau-corolis-interurbain-communaute-dagglomeration-du-beauvaisis",  # Confuses MOTIS
        "donnees-theoriques-et-temps-reel-du-reseau-axo-communaute-dagglomeration-creil-sud-oise",  # Confuses MOTIS
        "donnees-theoriques-et-temps-reel-du-reseau-sablons-bus-communaute-de-communes-des-sablons",  # Confuses MOTIS
        "donnees-theoriques-du-reseau-hopla-communaute-de-communes-de-la-plaine-destrees",  # Confuses MOTIS
        "tedbus-horaires",  # GTFS-RT tagges as GTFS
        "donnees-theoriques-et-temps-reel-du-reseau-le-bus-communaute-de-communes-du-clermontois",  # Confuses MOTIS
        "arrets-horaires-et-parcours-theoriques-gtfs-du-reseau-routier-regional-de-transport-scolaire-62-pas-de-calais",  # agency.txt
        "arrets-horaires-et-parcours-theoriques-gtfs-du-reseau-routier-regional-de-transport-interurbain-62-pas-de-calais",  # agency.txt
        "naolib-arrets-horaires-et-circuits",  # Incomplete read
        "offre-transport-du-reseau-txik-txak-nord-ex-chronoplus-gtfs",  # 404
        "horaires-theoriques-et-temps-reel-lignes-scolaires-sankeo-perpignan-gtfs-gtfs-rt",  # 404
        "reseau-cars-region-isere-38",  # empty, confuses MOTIS
    ]

    out: list[dict] = []
    for dataset in datasets:
        gtfs = list(filter(lambda r: "format" in r and (r["format"] == "GTFS" or r["format"] == "gtfs-rt"), dataset["resources"]))
        if gtfs:
            resources = list(filter(lambda r: "format" in r and r["format"] == "GTFS", gtfs))
            if not resources:
                print(f"{dataset['slug']} only has GTFS-RT data?", file=sys.stderr)
                continue

            source = {
                "name": dataset["slug"],
                "type": "http",
                "url": resources[0]["original_url"],
                "fix": True,
            }

            if dataset["slug"] in skip:
                source["skip"] = True

            if "page_url" in dataset:
                source["license"] = {}
                source["license"]["url"] = dataset["page_url"]

            out.append(source)

            def cond(r) -> bool:
                return "format" in r \
                    and r["format"] == "gtfs-rt" \
                    and "features" in r \
                    and "trip_updates" in r["features"]

            resources = list(filter(cond, gtfs))
            if not resources:
                continue
            if len(resources) > 1:
                print(f"{dataset['slug']} has multiple GTFS-RT feeds?",
                      file=sys.stderr)
                continue

            source = source.copy()
            source["spec"] = "gtfs-rt"
            source["type"] = "url"
            source["url"] = resources[0]["original_url"]
            del source["fix"]
            out.append(source)

    # This is an aggregated and improved feed that we want to keep
    out.append(
        {"name": "Brittany", "type": "transitland-atlas", "transitland-atlas-id": "f-gbwc-mobibreizh", "fix": True}
    )

    with open("feeds/fr.json", "r") as f:
        region = json.load(f)

    region["sources"] = out

    with open("feeds/fr.json", "w") as f:
        json.dump(region, f, indent=4, ensure_ascii=False)
