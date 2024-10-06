#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import json
import sys
import time
import os

from metadata import *
from pathlib import Path


def delete_file(path: Path):
    try:
        os.remove(path)
    except FileNotFoundError:
        print(f"Warning: Could not delete {path} because it did not exist")


if __name__ == "__main__":
    feeds_dir = Path("feeds/")
    out_dir = Path("out/")
    downloads_dir = Path("downloads/")

    referenced_filenames = []

    for region_file in feeds_dir.glob("*.json"):
        region_name = region_file.name[:region_file.name.rfind('.')]
        region = Region(json.load(open(region_file, "r")))
        for source in region.sources:
            source.name
            gtfs_filename = f"{region_name}_{source.name}.gtfs.zip"
            referenced_filenames.append(gtfs_filename)

    existing_out_filenames = [f.name for f in out_dir.glob("*.gtfs.zip")]

    to_delete_filenames = []

    for existing in existing_out_filenames:
        if existing not in referenced_filenames:
            to_delete_filenames.append(existing)

    if sys.stdout.isatty():
        print("The following files will be deleted in 5 seconds, " +
              "press Ctrl+C to cancel.")
        print([str(f) for f in to_delete_filenames])
        time.sleep(5)

    for f in to_delete_filenames:
        for p in [out_dir / f, downloads_dir / f]:
            if p.exists():
                delete_file(p)
