---
#template: home.html
title: Transitous
social:
  cards_layout_options:
    title: Free and Open Public Transport Routing
---

<!--
SPDX-FileCopyrightText: None
SPDX-License-Identifier: CC0-1.0
-->

# Transitous

Free and open public transport routing.

## Goal

A community-run provider-neutral international public transport routing service.

Using openly available GTFS/GTFS-RT/GBFS/etc. feeds and FOSS routing engine we want to operate a
routing service that:

* focuses on the interest of the user rather than the public transport operators
* is free to use
* values user privacy
* does not stop at borders
* aims at crowd-sourced maintenance of data feeds in the spirit of FOSS

## Contact

For general discussions about data availability: [#opentransport:matrix.org](https://matrix.to/#/#opentransport:matrix.org)

For Transitous-specific technical topics: [#transitous:matrix.spline.de](https://matrix.to/#/#transitous:matrix.spline.de)

## Used data

### Static timetables

The backbone of public transport routing is static [GTFS](https://gtfs.org) schedule data,
that's the bare minimum for Transitous to work in a region.

GTFS feeds ideally contain data for several months into the future, but can nevertheless receive
regular updates. Transitous checks for updates daily, so for this to work we also need
a stable URL for them.

For finding GTFS data, there's a few places worth looking at:

* The public transport operators themselves, they might just publish data on their website.
* Regional or national open data portals, especially in countries with regulation requiring public transport data to be published.
In the EU, those are called "National Access Point" (NAP).
* GTFS feed registries such as [Mobility Database](https://mobilitydatabase.org/) and [Transitland](https://www.transit.land/).
* Google Maps having public transport data in a region is a strong indicator whether GTFS feeds even exist,
as they use those as well.

### Realtime data

For properly dealing with delay, disruptions and all kinds of other unplanned
and short-notice service changes Transitous also uses [GTFS Realtime (RT)](https://gtfs.org/documentation/realtime/reference/) feeds.
Those are polled once a minute for updates.

GTFS-RT feeds come in three different flavors:

* Trip updates, that is realtime schedule changes like delays, cancellations, etc.
* Service alerts, that is textual descriptions of disruptions beyond a specific connection, such as upcoming construction work.
* Vehicle positions, that is geographic coordinates of the current position of trains or busses.

Transitous can handle the first two so far.

Note that GTFS-RT feeds typically only work in combination with a matching static GTFS feed. So e.g. combining a smaller realtime feed
of a single operator with a nationwide aggregated static feed will usually not work out of the box.

### Shared mobility data

Transitous doesn't just handle scheduled public transport though, but also vehicle sharing, which
can be particularly interesting for the first and last mile of a trip.

The data for this is provided by [GBFS](https://github.com/MobilityData/gbfs) feeds. This includes information about the type of vehicles (bikes,
cargo bikes, kickscooters, mopeds, cars, etc) and their method of propulsion (human powered, electric, etc),
where to pick them up and where to return them (same location as pickup, designated docks of the provider, free floating
within a specific area, etc) and most importantly where vehicles are currently available.

### On-demand services

Somewhere between scheduled transport and shared mobility are on-demand services. That is, services that require
some form or booking beforehand and might be anything from an on-demand bus that still follows a somewhat fixed
route with pre-defined stops to something closer to a taxi with a more flexible route that picks up or drops
off passengers anywhere in a given area.

These services are often used in times and/or areas with fewer demand, thus making them often the only mobility
option then/there. That makes it all the more important to have those covered as well.

Modeling on-demand services is challenging, given the variety on how those services work and their inherently very dynamic nature.
There's the relatively new [GTFS-Flex](https://gtfs.org/community/extensions/flex/) extension covering this. GTFS-Flex data might
be included in static GTFS data or provided separately.

### OSM

A crucial dataset for all road-based and in-building routing is [OpenStreetMap](https://openstreetmap.org). While that
is generally very comprehensive and up-to-date, there's one aspect that might need fixes, the floor level
separation. That's not visible in most OSM-based maps and thus is easy to miss while mapping. For Transitous this is
particularly important for in-building routing in train stations.

## Adding a region

Transitous data sources are divided by region, so they can be continuously tested and verified by locals.

All the data from a specific region is stored in a region file,
located in the [feeds](https://github.com/public-transport/transitous/tree/main/feeds) directory.
This region file is a `json` file, which is named after the unique country
[ISO_3166-1](https://en.wikipedia.org/wiki/ISO_3166-1) code or the unique principal subdivision
[ISO_3166-2](https://en.wikipedia.org/wiki/ISO_3166-2) code (for example for US states).

A region file has a `maintainers` attribute, which contains a list of people responsible for keeping the feeds for the region up to date.

```json
{
    "maintainers": [ ... ],
    "sources": [ ... ]
}
```

A person is represented like this:

```json
{
    "name": "< name of the maintainer >",
    "github": "< github username of the maintainer >"
}
```

The main attribute of a region is `sources`. It contains a list of feeds that should be fetched.

### Static feeds (timetable)

Each source can either be of `type` `mobility-database`, `transitland-atlas` or `http`.
Feeds from the [Mobility Database](https://mobilitydatabase.org/) can be referenced by the id in the URL on the website.
Feeds from [Transitland](https://www.transit.land/feeds) (a different database of feeds), can be referenced by their Onestop ID.

Mobility Database:
```json
{
    "name": "<name to be used for the output filename, should not contain spaces>",
    "type": "mobility-database",
    "mdb-id": "mdb-<number>"
}
```

Transitland:
```json
{
    "name": "<name to be used for the output filename, should not contain spaces>",
    "type": "transitland-atlas",
    "transitland-atlas-id": "<onestop id>"
}
```

If the feed is not part of any existing database, a http source can be used instead.

```json
{
    "name": "<name to be used for the output filename>",
    "type": "http",
    "url": "https://<url of GTFS file>",
    "license": {
        "spdx-identifier": "<license identifier from https://spdx.org/licenses/ if known>",
        "url": "< url as source for the license if available >"
    }
}
```

In both cases, the name needs to be unique in the file.
If the feed contains invalid entries, you can try to add the `"fix": true` attribute, to try to automatically correct errors.

### Realtime feeds

GTFS-RT feeds contain updates for a GTFS feed.
In order to know which feed to apply the updates to, their name must match the name of the static timetable.
Each source can either be of `type` `mobility-database`, `transitland-atlas` or `url`.
In the case of the `url` type, the field `spec` needs to be set to `gtfs-rt`.

This example applies the updates to the `lviv` feed:
```
[
    {
        "name": "lviv",
        "type": "http",
        "url": "https://track.ua-gis.com/gtfs/lviv/static.zip",
    },
    {
        "name": "lviv",
        "spec": "gtfs-rt",
        "type": "url",
        "url": "https://track.ua-gis.com/gtfs/lviv/trip_updates"
    }
]
```

### On-demand feeds

GTFS-Flex feeds can be added in the same way as regular GTFS feeds, just the `spec` field has to be set to `gtfs-flex`.

Example:
```json
{
    "name": "opentransportdataswiss-flex",
    "type": "http",
    "spec": "gtfs-flex",
    "url": "https://data.opentransportdata.swiss/en/dataset/gtfsflex/permalink",
    "license": {
        "url": "https://opentransportdata.swiss/de/terms-of-use/"
    }
}
```

### Shared Mobility feeds

GBFS feeds contains realtime information like vehicle availability and characteristics for shared Mobility (e.g. Bikesharing).
Each source can be of `type` `transitland-atlas` or `url`.
In the case of the `url` type, the field `spec` needs to be set to `gbfs`.

Feeds from [Transitland](https://www.transit.land/feeds) can be referenced by their Onestop ID.

Transitland:
```json
{
    "name": "<name of the feed>",
    "type": "transitland-atlas",
    "transitland-atlas-id": "<onestop id>"
}
```

Url:
```json
{
    "name": "<name of the feed>",
    "type": "url",
    "url": "https://<url of GBFS feed>",
    "spec": "gbfs"
}
```

The name needs to be unique in the file.

### Testing

Once you create a pull request, fetching your feed will automatically be tested.

You can also test it locally. For that, first get an up to date copy of transitland-atlas:

```bash
git submodule update --remote --checkout --init
```

You also need to have [gtfsclean](https://github.com/public-transport/gtfsclean) installed.
We provide a static build for linux so you don't need to build your own.

```
wget -P ~/.local/bin https://github.com/public-transport/gtfsclean/releases/latest/download/gtfsclean
chmod +x ~/.local/bin/gtfsclean
```

You can also use the container described below.

Then you can fetch individual regions using

```bash
./src/fetch.py feeds/<region>.json
```

### More source options

There are all kinds of options that may be specified in a source:

Option Name            | Description
---------------------- | ------------------------------------------------------------------------------------------------------------------------------------
`type`                 | `http`, `mobility-database`, `transitland-atlas` or `url`. Url sources are not downloaded, but passed to MOTIS as URL. This is used for realtime feeds.
`spec`                 | `gtfs` or `gtfs-rt`. `gtfs-rt` may only be used when `type` is `url`.
`fix`                  | Fix / drop fields that are not correct.
`skip`                 | Don't download or use this feed.
`skip-reason`          | Reason for why this feed can't be used right now.
`fix-csv-quotes`       | Try to fix GTFS files in which fields are improperly quoted. A symptom of this is if stop names start containing CSV.
`license`              | Dictionary of license-related options
`http-options`         | Dictionary of HTTP-related options
`drop-shapes`          | Remove route shapes, use if the shapes are mostly wrong
`drop-agency-names`    | Removes a list of agencies. Can be used to avoid duplicates if the agency provides its own feed.
`url-override`         | Use a different url instead of the one in Transitland / Mobility Database, or use a custom mirror. For more details, see the section on caches.
`display-name-options` | Specify which strings identifying a vehicle should be displayed to the user
`script`               | A Lua script applied by MOTIS to GTFS data during import, see [the MOTIS documentation](https://github.com/motis-project/motis/blob/master/docs/scripting.md) for details.

#### License Options

Option Name       | Description
----------------- | --------------------------------------------------
`spdx-identifier` | License identifier from <https://spdx.org/licenses/>
`url`             | Website that states the License of the data

#### HTTP Options

Option Name           | Description
--------------------- | -----------------------------------------------------------------------------------------------------------------------------
`headers`             | Dictionary of custom HTTP headers to send when checking for updates / downloading.
`ignore-tls-errors`   | Ignore expired / invalid TLS certificate
`fetch-interval-days` | Fetch this feed at most every `n` days. Useful if a server doesn't send `Last-Modified`, or to comply with terms of service.

#### Display Name Options

Option Name                 | Description
--------------------------- | -----------------------------------------------------------------------------------------------------------------------------
`copy-trip-names-matching`  | Regular expression specifying which values from `trip_short_name` should be displayed to the user.
`keep-route-names-matching` | Regular expression specifying which values from `route_short_name` should not be replaced even though the regular expression on `trip_short_name` matches.
`move-headsigns-matching`   | Regular expression specifying which values from `trip_headsign` should be moved to `route_short_name`. Mostly useful for SNCF.

```json
{
    "name": "OEBB",
    "type": "http",
    "url": "https://data.mobilitaetsverbuende.at/api/public/v1/data-sets/66/2025/file",
    "display-name-options": {
        "copy-trip-names-matching": "((IC)|(ECB)|(EC)|(RJ)|(RJX)|(D)|(NJ)|(EN)|(CJX)|(ICE)|(IR)|(REX)|(R)|(ER)|(ATB)) \\d+",
        "keep-route-names-matching": "((RE)|(RB)) \\d+"
    }
}
```

### Common Patterns

You can use `http-options` even with `transitland-atlas-id`.
This is useful for passing in things like headers with API keys.

```json
{
    "name": "Example-Feed",
    "type": "transitland-atlas",
    "transitland-atlas-id": "example-feed-id",
    "http-options": {
        "headers": {
            "api-key": "key"
        }
    }
}
```

## Diagnostics

There's a number of built-in and external tools available to inspect data sets and to check whether they
have been loaded correctly by Transitous.

### Static timetables

GTFS feeds are essentially ZIP files containing a set of CSV tables, making them relatively
easy to inspect e.g. with a spreadsheet application or text editor, although especially
nationwide aggregated feeds can get rather large.

Transitous might modify GTFS data as part of its import pipeline, you'll find the processed
feeds [here](https://api.transitous.org/gtfs/).

The [Transitous map view](https://api.transitous.org/) shows a colored markers for each (estimated)
current position of a public transport vehicle.

### Realtime data

GTFS-RT feeds use [Protocol Buffers](https://en.wikipedia.org/wiki/Protocol_Buffers), looking at their content
thus needs specialized tools.

``` bash
curl https://the.feed.url | protoc gtfs-realtime.proto --decode=transit_realtime.FeedMessage | less
```

The Protocol Buffers schema file needed for this can be downloaded [here](https://gtfs.org/documentation/realtime/gtfs-realtime.proto).

To see the realtime coverage available in Transitous, you can toggle the color coding of vehicles
on [its map view](https://api.transitous.org/) in the upper right corner. A green/yellow/red gradient shows the amount
of delay for the corresponding trip, while gray vehicles have no realtime information.

### Shared mobility data

GBFS consists of an entry point in form of a small JSON manifest that contains links to further JSON files with the actual information,
generally split up by how often certain aspects are expected to change.

Transitous currently has no built-in way to visualize availabe sharing vehicles.

### On-demand services

GTFS-Flex is an extension of GTFS static timetable data and as such is also a ZIP file containing CSV tables.
Additionally, it can also contain GeoJSON files defining regions that can be viewed e.g. with QGIS.

Tansitous' [map view in debug mode](https://api.transitous.org/?debug) does show GTFS-Flex zones when zooming in
far enough.

### OSM

When zoomed in enough the [map view of Transitous](https://api.transitous.org/) will offer you a floor level selector at the lower right.
That can give you a first indication if elements are misplaced (showing up on the wrong level) or not assigned to a floor level
at all (showing up on all levels). For reviewing smaller elements [indoor=](https://indoorequal.org) can also be useful,
and for fixing things [JOSM](https://josm.openstreetmap.de/) has a built-in level selector on the top left.

## Overview of the import pipeline
The following pipeline runs on a daily basis to import new GTFS feed data.
This image gives an overview of the steps executed in the data pipeline:
<img src="pipeline.svg" alt="diagram visualizing the data import pipeline">

## Caches

Due to varying uptime of the feed publishers' servers, feeds that are part of a database like Transitland or the Mobility Database are cached.

The fetching precedence is as follows:

1. If set, the url in `url-override` is tried first
2. The `url` is tried.
3. In case of a feed from a database, a cache is used. The cache url depends on the database.

## Running a transitous instance locally

Running a local instance of the transitous setup can be useful for debugging.
The easiest way is to use the same container image that we use for fetching and importing the data on the CI.

First, ensure that you have the Git submodules:

```bash
git submodule update --remote --checkout --init
```

Proceed by building the container:

```bash
podman build ci/container/ -t transitous -f ci/container/Containerfile
```

Enter the container:

```bash
podman run -it -p 8080:8080 -v $PWD:/transitous:Z --userns=keep-id -w /transitous transitous
```

Now inside the container, you can download and post-process the feeds you want.

```bash
./src/fetch.py feeds/<region>.json
```

If you want to download all of them instead, you can use `mkdir -p out && cd out && wget --mirror -l 1 --no-parent --no-directories --accept gtfs.zip -e robots=off https://api.transitous.org/gtfs/` to download the postprocessed files from the Transitous server, or `./ci/fetch-feeds.py timer` to process them yourself. However, importing all feeds will take about half an hour even on powerful hardware.

The `out/` directory should now contain a number of zip files.

In addition to those, you also need a background map. Importing the entire planet would take too long,
so for now, use a smaller region.
You can find working map pbf downloads at [Geofabrik](https://download.geofabrik.de/).
You can click on the region names to find downloads for smaller subregions.

Then download the chosen region:

```bash
wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -P out
```

In order to start motis, we need a config file listing all the feeds we want to use.
You can generate one using our script:

```bash
./src/generate-motis-config.py
```

The generated config file still needs a small adjustment.
Edit the line in `out/config.yml` that starts with `osm:` to point to your map, and remove the `coastline` option in `tiles`.

If you did not download all feeds, you also need to remove every feed that you did not download.
Thanks to the region code prefix, the part you want to keep should be easy to find.

You can then go to the `out` directory, import everything and start motis:

```bash
cd out
motis import
motis server
```

Once it's done, the motis web interface should be reachable on [localhost:8080](http://localhost:8080).


