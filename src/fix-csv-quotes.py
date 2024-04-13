#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import zipfile
import sys
import os
from functools import reduce
import csv
import io


def strip_quotes(field: str):
    if field.startswith('"') and field.endswith('"'):
        return field[1:-1]
    else:
        return field


def parse_fuzzy_csv(csv: str) -> list[list[str]]:
    rows = []
    for line in csv.splitlines():
        line = line.decode()
        start = 0
        current_field_start = 0
        fields = []
        while True:
            fieldsep = line.find(",", start)
            if fieldsep == -1:
                field = line[current_field_start:]
                fields.append(strip_quotes(field.strip()))
                rows.append(fields)
                break

            field = line[current_field_start:fieldsep]
            numquotes = reduce(
                lambda acc, c: acc + 1 if c == '"' else acc, field, 0)
            if numquotes % 2 == 0:
                fields.append(strip_quotes(field.strip()))
                current_field_start = fieldsep + 1
                start = fieldsep + 1
            else:
                current_field_start = start
                start = fieldsep + 1

    return rows


def edit_zip(source: str, destination: str):
    with zipfile.ZipFile(source) as inzip, \
            zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as outzip:
        # Iterate the input files
        for inzipinfo in inzip.infolist():
            with inzip.open(inzipinfo) as infile:
                if inzipinfo.filename.endswith(".txt"):
                    print("Rewriting", inzipinfo.filename)
                    content = infile.read()
                    rows = parse_fuzzy_csv(content)

                    with io.StringIO() as outcsv:
                        writer = csv.writer(outcsv)
                        for row in rows:
                            writer.writerow(row)

                        outzip.writestr(inzipinfo.filename, outcsv.getvalue())
                else:
                    outzip.writestr(inzipinfo.filename, infile.read())


if __name__ == "__main__":
    source = sys.argv[1]
    destination = source + ".tmp"

    edit_zip(source, destination)

    os.rename(destination, source)
