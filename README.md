# Transitous

Free and open public transport routing.

## Goal

A community-run provider-neutral international public transport routing service.

Using openly available GTFS/GTFS-RT/etc feeds and FOSS routing engine we want to operate a
routing service that:
* focuses on the interest of the user rather than the public transport operators
* is free to use
* values user privacy
* does not stop at borders
* aims at crowd-sourced maintenance of data feeds in the spirit of FOSS

## Docker development install
```
git submodule update
docker-compose up -d
```
### Import new feed
```
docker-compose run --rm motis transitous fetch <feed-file-name>
```


Note than docker volume "input" is filled within the first start. If you make changes you have to delete the volume.

**Attention: Data lost!**
```
docker-compose down -v
docker-compose up -d --build
```



## Contact

* Matrix channel: [#opentransport:matrix.org](https://matrix.to/#/#opentransport:matrix.org) (for now)

<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: none
-->
