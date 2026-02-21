#!/usr/bin/env python3
# SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import csv
from ruamel.yaml import YAML
import pathlib
import requests
import os

parser = argparse.ArgumentParser(description='Transitous meta-station GTFS feed generator.')
parser.add_argument('--config', type=str, help="Configuration file describing the meta station mapping", default="metastations/metastations.yml")
parser.add_argument('--output', type=str, help="GTFS feed output folder", default="out/transitous_meta")
arguments = parser.parse_args()


if __name__ == "__main__":

    stops = []
    stop_groups = []
    translations = []
    with open(arguments.config) as f:
        yaml = YAML(typ="rt")
        config = yaml.load(f)

        headers = {"User-Agent": "org.transitous.metastation-generator"}
        for metastation in config:
            print(metastation)
            metareq = requests.get(f"https://www.wikidata.org/w/rest.php/wikibase/v1/entities/items/{metastation}/labels", headers=headers)
            metadata = metareq.json()
            stop = {
                "stop_id": metastation,
                "stop_name": metadata["en"],
                "stop_lat": 0,
                "stop_lon": 0,
                "location_type": 0
            }
            stops.append(stop)

            for lang, name in metadata.items():
                if len(lang) != 2 or (lang != "en" and name == metadata["en"]):
                    continue
                translation = {
                    "table_name": "stops",
                    "field_name": "stop_name",
                    "language": lang,
                    "record_id": metastation,
                    "translation": name
                }
                translations.append(translation)

            for station in config[metastation]:
                print(station)
                stationreq = requests.get(f"https://www.wikidata.org/w/rest.php/wikibase/v1/entities/items/{station}", headers=headers)
                stationdata = stationreq.json()
                coord = stationdata["statements"]["P625"][0]["value"]["content"]
                stop = {
                    "stop_id": station,
                    "stop_name": stationdata["labels"]["en"],
                    "stop_lat": coord["latitude"],
                    "stop_lon": coord["longitude"],
                    "location_type": 0
                }
                stops.append(stop)
                stop_group = {
                    "stop_group_id": metastation,
                    "stop_id": station,
                }
                stop_groups.append(stop_group)

    os.makedirs(arguments.output, exist_ok=True)

    # create dummy files we need for MOTIS to recognize this as a valid GTFS feed
    pathlib.Path(os.path.join(arguments.output, "calendar_dates.txt")).touch(exist_ok=True)
    pathlib.Path(os.path.join(arguments.output, "routes.txt")).touch(exist_ok=True)
    pathlib.Path(os.path.join(arguments.output, "stop_times.txt")).touch(exist_ok=True)
    pathlib.Path(os.path.join(arguments.output, "trips.txt")).touch(exist_ok=True)

    # dummy agency data to define a timezone
    agency = {
        "agency_id": "transitous",
        "agency_name": "Transitous",
        "agency_url": "https://transitous.org",
        "agency_timezone": "Etc/UTC",
    }
    with open(os.path.join(arguments.output, "agency.txt"), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=agency.keys())
        writer.writeheader()
        writer.writerow(agency)

    # write stops
    with open(os.path.join(arguments.output, "stops.txt"), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=["stop_id", "stop_name", "stop_lat", "stop_lon", "location_type"])
        writer.writeheader()
        for stop in stops:
            writer.writerow(stop)

    # write stop_group_elements
    with open(os.path.join(arguments.output, "stop_group_elements.txt"), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=["stop_group_id", "stop_id"])
        writer.writeheader()
        for group in stop_groups:
            writer.writerow(group)

    # write translations
    with open(os.path.join(arguments.output, "translations.txt"), 'w') as f:
        writer = csv.DictWriter(f, fieldnames=["table_name", "field_name", "language", "record_id", "translation"])
        writer.writeheader()
        for t in translations:
            writer.writerow(t)
