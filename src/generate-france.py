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

    skip = ["blablacar-bus-horaires-theoriques-et-temps-reel-du-reseau-europeen",
            "flixbus-horaires-theoriques-du-reseau-europeen-1",
            "gtfs-static-et-real-time-transporteur-thalys",
            "eurostar-gtfs",
            "arrets-horaires-et-parcours-theoriques-du-reseau-routier-regional-de-transport-scolaire-et-interurbain-60-oise",  # broken
            "horaires-prevus-sur-les-lignes-de-transport-en-commun-dile-de-france-gtfs-jeux-olympiques-et-paralympiques-de-paris-2024-datahub", # try removing
            "horaires-theoriques-des-cars-du-rhone"  # requires authentication
            ]

    out: list[dict] = []
    for dataset in datasets:
        if dataset["slug"] in skip:
            continue

        gtfs = list(filter(lambda r: "format" in r and r["format"] == "GTFS",
                           dataset["resources"]))
        if gtfs:
            resource = gtfs[0]
            source = {
                "name": dataset["slug"],
                "type": "http",
                "url": resource["original_url"],
                "fix": True
            }

            if "licence" in dataset and dataset["licence"] != "notspecified":
                source["license"] = dataset["licence"]

            out.append(source)

    json.dump(out, indent=4, fp=sys.stdout)
