#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import requests
import json
import sys


if __name__ == "__main__":
    datasets = requests.get("https://transport.data.gouv.fr/api/datasets") \
        .json()

    skip = ["blablacar-bus-horaires-theoriques-et-temps-reel-du-reseau-europeen", # Already in eu.json
            "flixbus-horaires-theoriques-du-reseau-europeen-1", # Already in eu.json
            "gtfs-static-et-real-time-transporteur-thalys", # Already in eu.json
            "eurostar-gtfs", # Already in eu.json
            "arrets-horaires-et-parcours-theoriques-du-reseau-routier-regional-de-transport-scolaire-et-interurbain-60-oise",  # broken
            "horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs-jeux-olympiques-et-paralympiques-de-paris-2024-datahub", # try removing
            "horaires-theoriques-des-cars-du-rhone",  # requires authentication
            "horaires-theoriques-des-lignes-scolaires-du-reseau-transports-en-commun-lyonnais", # requires authentication
            "horaires-theoriques-du-reseau-libellule-sytral-de-la-communaute-dagglomeration-de-villefranche-beaujolais-saone", # requires authentication
            "horaires-theoriques-du-reseau-transports-en-commun-lyonnais",
            "description-de-loffre-tad-tao-gtfs-flex-orleans-metropole",
            "reseau-de-bus-urbain-horizon", # 404 not found
            "horaires-theoriques-et-temps-reel-de-la-navette-du-pont-de-saint-nazaire-gtfs-gtfs-rt",
            "horaires-theoriques-de-la-navette-velo-du-pont-de-saint-nazaire-gtfs",  # no agency.txt
            "horaires-theoriques-et-temps-reel-des-navettes-de-la-ligne-bagneres-la-mongie-gtfs-gtfs-rt",  # 404 not found
            "horaires-theoriques-et-temps-reel-des-navettes-de-la-station-de-tignes-gtfs-gtfs-rt",
            "horaires-theoriques-et-temps-reel-des-navettes-de-val-disere-gtfs-gtfs-rt", # 404 not found
            "horaires-theoriques-et-temps-reel-des-navettes-hivernales-de-lalpe-dhuez-gtfs-gtfs-rt", # 404 not found
            "arrets-horaires-et-parcours-theoriques-des-bus-du-reseau-des-transports-publics-envibus", # timeout
            "fr-horaires-theoriques-du-service-rhonexpress-de-la-metropole-de-lyon-et-du-departement-du-rhone" # 401 not authorized
            ]

    out: list[dict] = []
    for dataset in datasets:
        gtfs = list(filter(lambda r: "format" in r and r["format"] == "GTFS",
                           dataset["resources"]))
        if gtfs:
            resource = gtfs[0]
            source = {
                "name": dataset["slug"],
                "type": "http",
                "url": resource["original_url"],
                "fix": True,
            }

            if dataset["slug"] in skip:
                source["skip"] = True

            if "licence" in dataset and dataset["licence"] != "notspecified":
                source["license"] = dataset["licence"]

            out.append(source)

    json.dump(out, indent=4, fp=sys.stdout)
