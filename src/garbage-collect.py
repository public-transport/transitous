#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Utility script to remove GTFS archives that are no longer referenced
by any region feed configuration.

The script scans all JSON feed definitions in the ``feeds/`` directory,
collects the list of GTFS zip files that are still in use, and then
deletes any matching files that remain in the ``out/`` and
``downloads/`` directories but are no longer referenced.
"""

import json
import sys
import time
import os

from metadata import Region
from pathlib import Path


def delete_file(path: Path) -> None:
    """
    Delete the file at the given path, printing a warning if it does not exist.

    Parameters
    ----------
    path : Path
        Absolute or relative path to the file that should be removed.
    """
    try:
        os.remove(path)
    except FileNotFoundError:
        print(f"Warning: Could not delete {path} because it did not exist")


if __name__ == "__main__":
    # Directories containing the region definitions and GTFS archives.
    feeds_dir = Path("feeds/")
    out_dir = Path("out/")
    downloads_dir = Path("downloads/")

    # List of GTFS filenames that are still referenced by at least one region.
    referenced_filenames: list[str] = []

    # Build the list of referenced GTFS archives from all region JSON files.
    for region_file in feeds_dir.glob("*.json"):
        region_name = region_file.stem
        with region_file.open("r", encoding="utf-8") as f:
            region = Region(json.load(f))

        for source in region.sources:
            gtfs_filename = f"{region_name}_{source.name}.gtfs.zip"
            referenced_filenames.append(gtfs_filename)

    # Collect all GTFS archives currently present in the output directory.
    existing_out_filenames = [f.name for f in out_dir.glob("*.gtfs.zip")]

    # Determine which files are no longer referenced and can be removed.
    to_delete_filenames: list[str] = [
        existing for existing in existing_out_filenames
        if existing not in referenced_filenames
    ]

    # If running in an interactive terminal, show a short preview and delay
    # so the user has a chance to cancel before files are removed.
    if sys.stdout.isatty() and to_delete_filenames:
        print(
            "The following files will be deleted in 5 seconds, "
            "press Ctrl+C to cancel."
        )
        print([str(f) for f in to_delete_filenames])
        time.sleep(5)

    # Delete each obsolete archive from both the output and downloads folders.
    for filename in to_delete_filenames:
        for path in (out_dir / filename, downloads_dir / filename):
            if path.exists():
                delete_file(path)
