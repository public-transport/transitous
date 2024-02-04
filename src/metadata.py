from typing import List, Union


class Maintainer:
    name: str
    email: str

    @staticmethod
    def fromJson(parsed: dict):
        maintainer = Maintainer()
        maintainer.name = parsed["name"]
        maintainer.email = parsed["email"]
        return maintainer


class TransitlandSource:
    transitland_atlas_id: str

    @staticmethod
    def fromJson(parsed: dict):
        source = TransitlandSource()
        source.transitland_atlas_id = parsed["transitland-atlas-id"]
        return source


class HttpSource:
    url: str

    @staticmethod
    def fromJson(parsed: dict):
        source = HttpSource()
        source.url = parsed["url"]
        return source


Source = Union[TransitlandSource, HttpSource]


def sourceFromJson(parsed: dict) -> Source:
    match parsed["type"]:
        case "transitland-atlas":
            return TransitlandSource.fromJson(parsed)
        case "http":
            return HttpSource.fromJson(parsed)

    return None


class Region:
    maintainers: List[Maintainer]
    sources: Source

    @staticmethod
    def fromJson(parsed: dict):
        region = Region()
        region.maintainers = map(Maintainer.fromJson, parsed["maintainers"])
        region.sources = map(sourceFromJson, parsed["sources"])
        return region
