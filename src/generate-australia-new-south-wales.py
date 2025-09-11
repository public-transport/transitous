#!/usr/bin/env python3
# SPDX-FileCopyrightText: applecuckoo <nufjoysb@duck.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# generate-australia-new-south-wales.py - blocklist generator for TfNSW 'complete' feed

import csv
from io import StringIO
import json
import requests

def clean_text(text) -> str:
    return text.replace('\u0092', '').replace('\u00a0', '')

# pull resource ID from TfNSW CKAN instance and get latest URL
ckan_url = 'https://opendata.transport.nsw.gov.au/api/3/action/resource_show?id=30b850b7-f439-4e30-8072-e07ef62a2a36'
ckan = requests.get(ckan_url).json()
lookup_table_url = ckan['result']['url']
lookup_table = requests.get(lookup_table_url)
lookup_table.encoding = 'iso-8859-1'
lookup_table = clean_text(lookup_table.text)
lookup = csv.DictReader(StringIO(lookup_table.split('\n', 1)[1]))

blocklist = []
for rows in lookup:
    rt_agency = rows['For Realtime GTFS agency_name'].strip()
    if rt_agency != '' and rt_agency not in blocklist:
        blocklist.append(rows['Complete GTFS agency_name'].strip())

with open('feeds/au-nsw.json', 'r') as f:
    region = json.load(f)

region['sources'][0]['drop-agency-names'] = blocklist

with open("feeds/au-nsw.json", "w") as f:
    json.dump(region, f, indent=4, ensure_ascii=False)
