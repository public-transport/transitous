# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional


class Maintainer:
    name: str
    email: str

    def __init__(self, parsed: dict):
        self.name = parsed["name"]
        self.email = parsed["email"]


class License:
    spdx_identifier: Optional[str] = None
    url: Optional[str] = None


class Source:
    name: str
    fix: bool = False
    license: Optional[License] = None
    spec: str = "gtfs"
    enabled: bool = True

    def __init__(self, parsed: dict = None):
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
            if "spec" in parsed:
                self.spec = parsed["spec"]


class HttpOptions:
    fetch_interval_days: Optional[int] = None


class TransitlandSource(Source):
    transitland_atlas_id: str
    options: HttpOptions = HttpOptions()
    url_override: str

    def __init__(self, parsed: dict):
        super().__init__(parsed)
        self.transitland_atlas_id = parsed["transitland-atlas-id"]
        self.url_override = parsed.get("url-override", None)

        if "options" in parsed:
            options = parsed["options"]
            if "fetch-interval-days" in options:
                self.options.fetch_interval_days = \
                    int(parsed["options"]["fetch-interval-days"])


class HttpSource(Source):
    url: str
    options: HttpOptions = HttpOptions()

    def __init__(self, parsed: dict = None):
        if parsed:
            super().__init__(parsed)
            self.url = parsed["url"]

            if "options" in parsed:
                options = parsed["options"]
                if "fetch-interval-days" in options:
                    self.options.fetch_interval_days = \
                        int(parsed["options"]["fetch-interval-days"])


class UrlSource(Source):
    url: str
    authorization: str = None

    def __init__(self, parsed: dict = None):
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

    return None


class Region:
    maintainers: List[Maintainer]
    sources: Source

    def __init__(self, parsed: dict):
        self.maintainers = map(Maintainer, parsed["maintainers"])
        self.sources = map(sourceFromJson, parsed["sources"])
