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
    enabled: bool = True
    fix_csv_quotes: bool = False

    def __init__(self, parsed: Optional[dict] = None):
        self.license = License()
        if parsed:
            if "enabled" in parsed:
                self.enabled = bool(parsed["enabled"])

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


class HttpOptions:
    fetch_interval_days: Optional[int] = None
    headers: dict[str, str] = {}
    ignore_tls_errors: bool = False


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

        if "options" in parsed:
            options = parsed["options"]
            if "fetch-interval-days" in options:
                self.options.fetch_interval_days = \
                    int(parsed["options"]["fetch-interval-days"])
            if "ignore-tls-errors" in options:
                self.options.ignore_tls_errors = \
                    bool(parsed["options"]["ignore-tls-errors"])

        if "http-headers" in parsed:
            for key in parsed["http-headers"]:
                self.options.headers[key] = parsed["http-headers"][key]


class HttpSource(Source):
    url: str = ""
    options: HttpOptions = HttpOptions()
    url_override: Optional[str] = None

    def __init__(self, parsed: Optional[dict] = None):
        if parsed:
            super().__init__(parsed)
            self.url = parsed["url"]
            self.url_override = parsed.get("url-override", None)

            if "options" in parsed:
                options = parsed["options"]
                if "fetch-interval-days" in options:
                    self.options.fetch_interval_days = \
                        int(parsed["options"]["fetch-interval-days"])
                if "ignore-tls-errors" in options:
                    self.options.ignore_tls_errors = \
                        bool(parsed["options"]["ignore-tls-errors"])

            if "http-headers" in parsed:
                for key in parsed["http-headers"]:
                    self.options.headers[key] = parsed["http-headers"][key]


class UrlSource(Source):
    url: str = ""
    authorization: Optional[str] = None

    def __init__(self, parsed: Optional[dict] = None):
        if parsed:
            super().__init__(parsed)
            self.url = parsed["url"]
            if "authorization" in parsed:
                self.authorization = parsed["authorization"]


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
