#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
import json
import metadata
import os
import shutil
import sys
import transitland
import mobilitydatabase
import subprocess

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
from typing import Any
from pathlib import Path
from utils import eprint
from urllib.parse import quote

# replace in result:
#  |
#      !vault |

def migrate_headers(id, source, secrets):
    if 'headers' in source:
        new_headers = {
            'headers' : {}
        }
        for key, value in source['headers'].items():
            r = subprocess.run(["ansible-vault", "encrypt_string", "--vault-id", "feed-proxy@/etc/feed-proxy.vault", value], capture_output = True, text = True) 
            new_headers['headers'][key] = LiteralScalarString(r.stdout)

        secrets[id] = new_headers
        source['headers'] = {}
        if 'skip' in source:
            del source['skip']
        if 'skip-reason' in source:
            del source['skip-reason']
        source['use-feed-proxy'] = True
        return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Feed Proxy migration')
    parser.add_argument('regions', type=str, help='Only generate configuration for the given region(s) (leave empty for all regions, globs are supported)', nargs="*")
    arguments = parser.parse_args()

    feed_dir = Path("feeds/")
    script_dir = Path("scripts/")
    rt_list = {}

    with open("ansible/roles/feed-proxy/vars/feed-secrets.yml", "r") as fo:
        yaml = YAML(typ="rt")

        secrets = yaml.load(fo)

        feeds = []
        if len(arguments.regions) == 0:
            feeds = feed_dir.glob("*.json")
        else:
            for region in arguments.regions:
                feeds += feed_dir.glob(f"{region}.json")

        for feed in sorted(feeds):
            print(feed)
            touched = False
            with open(feed, "r") as f:
                
                parsed = json.load(f)

                metadata_filename = feed.name
                region_name = metadata_filename[: metadata_filename.rfind(".")]

                for source in parsed['sources']:
                    schedule_name = f"{region_name}-{source['name']}"

                    if 'spec' not in source:
                        continue
                    match source["spec"]:
                        case "gtfs-rt":
                            name = f"{region_name}-{source['name']}"

                            if name not in rt_list:
                                rt_list[name] = 0

                            if migrate_headers(name + "-" + str(rt_list[name]), source, secrets):
                                touched = True

                            rt_list[name] += 1

                        case "gbfs":
                            name = f"{region_name}-{source['name']}"
                            migrate_headers(name, source, secrets)
                            source['use-feed-proxy'] = True
                            touched = True
                if touched:
                    with open(feed, "w") as f:
                        json.dump(parsed, f, indent=4, ensure_ascii=False)

        with open("ansible/roles/feed-proxy/vars/feed-secrets.yml", "w") as fo:                
            yaml.dump(secrets, fo)