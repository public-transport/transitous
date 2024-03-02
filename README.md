<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: none
-->

# Transitous

Free and open public transport routing.

## Goal

A community-run provider-neutral international public transport routing service.

Using openly available GTFS/GTFS-RT/etc. feeds and FOSS routing engine we want to operate a
routing service that:
* focuses on the interest of the user rather than the public transport operators
* is free to use
* values user privacy
* does not stop at borders
* aims at crowd-sourced maintenance of data feeds in the spirit of FOSS

## Contact

* Matrix channel: [#opentransport:matrix.org](https://matrix.to/#/#opentransport:matrix.org) (for now)

## Adding a region

Transitous data sources are divided by region, so they can be continuously tested and verified by locals.

A region file in the [feeds](feeds) directory has a `maintainers` attribute, which contains a list of people responsible for keeping the feeds for the region up to date.

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

Each source can either be of `type` "transitland-atlas" or "http".
A transitland-atlas source is a feed from [Transitland](https://www.transit.land/feeds), identified by its Onestop ID.

```json
{
    "name": "<name to be used for the output filename, should not contain spaces>",
    "type": "transitland-atlas",
    "transitland-atlas-id": "<onestop id>"
}
```

If the feed is not known in Transitland, a http source can be used instead.

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

In both cases, the name needs to be unique in the file, except for if it is an GTFS-RT feed. These are realtime feeds that contain updates for a GTFS feed.
In order to know which one to apply the updates to, the names must match.

If the feed contains errors, you can try to add the `"fix": true` attribute, to try to automatically correct errors.

Once you create a pull request, fetching your feed will automatically be tested.

You can also test it locally, by running `./src/fetch.py feeds/<region>.json`.

For that you need to have [gtfstidy](https://github.com/patrickbr/gtfstidy) installed.
You can also use the container described below.


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
podman run -it --privileged -p 8080:8080 -v $PWD:/transitous -w /transitous transitous
```

Now inside the container, you can download and post-process all the feeds. This may take a while.
```bash
./ci/fetch-feeds.py timer
```

The `out/` directory should now contain a number of zip files.

In addition to those, you also need a background map. Importing all of europe would take too long,
so for now just a smaller region.
You can find working map pbf downloads at [Geofabrik](https://download.geofabrik.de/).
You can click on the region names to find downloads for smaller subregions.

Then download the chosen region:
```bash
wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -P out
```

In order to start motis, we need a config file listing all the feeds we want to use.
You can generate one using our script:
```bash
./src/generate-motis-config.py full
```

The generated config file still needs a small adjustment.
Edit the line in `out/config.ini` that starts with `paths=osm` to point to your map.

You can then go to the `out` directory, and start motis:
```bash
cd out
motis -c config.ini --server.host 0.0.0.0 --server.static_path /opt/motis/web
```

The first start will take a while, as it imports all the maps and feeds.
Once it's done, the motis web interface should be reachable on [localhost:8080](http://localhost:8080).
