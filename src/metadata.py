# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional
from utils import eprint

import sys


class Maintainer:
    name: str
    github: str

    def __init__(self, parsed: dict):
        self.name = parsed["name"]
        self.github = parsed["github"]


class License:
    spdx_identifier: Optional[str] = None
    url: Optional[str] = None


class Source:
    name: str
    fix: bool = False
    license: Optional[License] = None
    spec: str = "gtfs"
    fix_csv_quotes: bool = False
    skip: bool = False
    skip_reason: str = ""
    function: Optional[str] = None
    drop_too_fast_trips: bool = True
    drop_shapes: bool = False
    drop_agency_names: List[str] = []

    def __init__(self, parsed: Optional[dict] = None):
        self.license = License()
        if parsed:
            if "license" in parsed:
                if "spdx-identifier" in parsed["license"]:
                    self.license.spdx_identifier = parsed["license"]["spdx-identifier"]
                if "url" in parsed["license"]:
                    self.license.url = parsed["license"]["url"]

            self.name = parsed["name"]
            if "fix" in parsed:
                self.fix = bool(parsed["fix"])
            if "fix-csv-quotes" in parsed:
                self.fix_csv_quotes = bool(parsed["fix-csv-quotes"])
            if "spec" in parsed:
                self.spec = parsed["spec"]
            if "skip" in parsed:
                self.skip = bool(parsed["skip"])
            if "skip-reason" in parsed:
                self.skip_reason = parsed["skip-reason"]
            if "function" in parsed:
                self.function = parsed["function"]
            if "drop-too-fast-trips" in parsed:
                self.drop_too_fast_trips = parsed["drop-too-fast-trips"]
            if "drop-shapes" in parsed:
                self.drop_shapes = parsed["drop-shapes"]
            if "drop-agency-names" in parsed:
                self.drop_agency_names = parsed["drop-agency-names"]


class HttpOptions:
    fetch_interval_days: Optional[int] = None
    headers: dict[str, str] = {}
    ignore_tls_errors: bool = False

    def __init__(self, parsed: Optional[dict] = None):
        if parsed:
            if "fetch-interval-days" in parsed:
                self.fetch_interval_days = \
                    int(parsed["fetch-interval-days"])
            if "ignore-tls-errors" in parsed:
                self.ignore_tls_errors = \
                    bool(parsed["ignore-tls-errors"])
            if "headers" in parsed:
                for key in parsed["headers"]:
                    self.headers[key] = parsed["headers"][key]


class TransitlandSource(Source):
    transitland_atlas_id: str = ""
    options: HttpOptions = HttpOptions()
    url_override: Optional[str] = None
    proxy: bool = False

    def __init__(self, parsed: dict):
        super().__init__(parsed)
        self.transitland_atlas_id = parsed["transitland-atlas-id"]
        self.url_override = parsed.get("url-override", None)
        self.proxy = parsed.get("proxy", False)

        if "http-options" in parsed:
            self.options = HttpOptions(parsed["http-options"])


class HttpSource(Source):
    url: str = ""
    options: HttpOptions = HttpOptions()
    url_override: Optional[str] = None

    def __init__(self, parsed: Optional[dict] = None):
        if parsed:
            super().__init__(parsed)
            self.url = parsed["url"]
            self.url_override = parsed.get("url-override", None)

            if "http-options" in parsed:
                self.options = HttpOptions(parsed["http-options"])


class UrlSource(Source):
    url: str = ""
    headers: Optional[dict[str, str]] = None

    def __init__(self, parsed: Optional[dict] = None):
        if parsed:
            super().__init__(parsed)
            self.url = parsed["url"]
            if "headers" in parsed:
                self.headers = parsed["headers"]


def sourceFromJson(parsed: dict) -> Source:
    match parsed["type"]:
        case "transitland-atlas":
            return TransitlandSource(parsed)
        case "http":
            return HttpSource(parsed)
        case "url":
            return UrlSource(parsed)

    eprint("Error: Unknown value for type:", parsed["type"])
    eprint("Allowed values: transitland-atlas, http, url")
    sys.exit(1)


class Region:
    maintainers: List[Maintainer] = []
    sources: List[Source] = []

    def __init__(self, parsed: dict):
        self.maintainers = list(map(Maintainer, parsed["maintainers"]))
        self.sources = list(map(sourceFromJson, parsed["sources"]))
