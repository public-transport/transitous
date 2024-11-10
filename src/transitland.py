# SPDX-FileCopyrightText: 2023 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path
from typing import Dict, Union, Optional
import json
from metadata import UrlSource, HttpSource, Source, TransitlandSource, License
import sys


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

    def source_by_id(self, source: TransitlandSource) -> Union[Source, None]:
        result: Optional[Source] = None
        feed = self.by_id[source.transitland_atlas_id]
        if "static_current" in feed["urls"]:
            result = HttpSource()
            result.name = source.name
            result.url = feed["urls"]["static_current"]
            result.options = source.options
            result.spec = "gtfs"
            result.fix = source.fix
            result.skip = source.skip
            result.skip_reason = source.skip_reason
            result.drop_too_fast_trips = source.drop_too_fast_trips
            result.function = source.function
            result.drop_shapes = source.drop_shapes

            if source.url_override:
                result.url_override = source.url_override

            if source.proxy:
                result.url_override = "https://gtfsproxy.fwan.it/" + \
                    source.transitland_atlas_id

        elif "realtime_trip_updates" in feed["urls"]:
            result = UrlSource()
            result.name = source.name
            result.url = feed["urls"]["realtime_trip_updates"]
            result.spec = "gtfs-rt"
            result.skip = source.skip
            result.skip_reason = source.skip_reason
        else:
            print("Warning: Found Transitland source that we can't handle:", source.transitland_atlas_id)
            sys.stdout.flush()
            return None

        if "license" in feed:
            result.license = License()
            if "spdx_identifier" in feed["license"]:
                result.license.spdx_identifier = feed["license"]["spdx_identifier"]
            if "url" in feed["license"]:
                result.license.url = feed["license"]["url"]

        return result
