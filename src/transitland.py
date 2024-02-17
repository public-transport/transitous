# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path
from typing import Dict
import json
from metadata import *


class Atlas:
    by_id: Dict[str, dict]

    def __init__(self):
        self.by_id = {}

    @staticmethod
    def load(path: Path):
        atlas = Atlas()
        for f in Path(path / "feeds").iterdir():
            for feed in json.load(open(f, "r"))["feeds"]:
                atlas.by_id[feed["id"]] = feed

        return atlas

    def source_by_id(self, source: TransitlandSource) -> HttpSource:
        feed = self.by_id[source.transitland_atlas_id]
        http_source = HttpSource()
        http_source.name = source.name
        http_source.url = feed["urls"]["static_current"]

        if "license" in feed:
            http_source.license = License()
            if "spdx_identifier" in feed["license"]:
                http_source.license.spdx_identifier = feed["license"]["spdx_identifier"]
            if "url" in feed["license"]:
                http_source.license.url = feed["license"]["url"]

        return http_source
