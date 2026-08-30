#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Johannes Grof <contact@johannesgrof.me>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Blank trip headsigns matching a regular expression.

Some feeds export a placeholder instead of a destination, e.g. "0". MOTIS
substitutes the last stop of a trip for headsigns that are empty when the
GTFS is parsed, so clearing the field here restores a usable destination.
Clearing it from an import script does not work: the substitution happens
before the script stage runs.
"""

import csv
import io
import os
import re
import sys
import zipfile

HEADSIGN_COLUMN = "trip_headsign"


def blank_headsigns(content: bytes, pattern: re.Pattern) -> tuple[bytes, int]:
    reader = csv.reader(io.StringIO(content.decode("utf-8-sig")))
    rows = list(reader)
    if not rows:
        return content, 0

    header = rows[0]
    if HEADSIGN_COLUMN not in header:
        return content, 0

    column = header.index(HEADSIGN_COLUMN)
    blanked = 0
    for row in rows[1:]:
        if column < len(row) and pattern.fullmatch(row[column]):
            row[column] = ""
            blanked += 1

    if blanked == 0:
        return content, 0

    with io.StringIO(newline="") as out:
        csv.writer(out, lineterminator="\r\n").writerows(rows)
        return out.getvalue().encode(), blanked


def edit_zip(source: str, destination: str, pattern: re.Pattern) -> int:
    blanked = 0
    with zipfile.ZipFile(source) as inzip, \
            zipfile.ZipFile(destination, "w",
                            compression=zipfile.ZIP_DEFLATED) as outzip:
        for info in inzip.infolist():
            with inzip.open(info) as infile:
                content = infile.read()
                if os.path.basename(info.filename) == "trips.txt":
                    content, blanked = blank_headsigns(content, pattern)
                outzip.writestr(info, content)
    return blanked


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <gtfs.zip> <regex>", file=sys.stderr)
        sys.exit(1)

    archive = sys.argv[1]
    pattern = re.compile(sys.argv[2])
    destination = archive + ".tmp"

    blanked = edit_zip(archive, destination, pattern)
    os.rename(destination, archive)

    print(f"Blanked {blanked} headsigns matching {pattern.pattern}")
