#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"

cd /var/lib/motis
chown -R motis:motis /var/lib/motis/
sudo -u motis wget --limit-rate=30m --mirror -l 2 --no-parent --cut-dirs=1 --no-host-directories --include-directories=gtfs,gtfs/scripts --accept gtfs.zip --accept .lua --accept config.yml --accept .import-running -e robots=off https://api.transitous.org/gtfs/ || true
sudo -u motis sed -i 's/planet-latest.osm.pbf/liechtenstein-latest.osm.pbf/g' /var/lib/motis/config.yml
sudo -u motis sed -i '/coastline:/d' /var/lib/motis/config.yml
sudo -u motis /opt/motis/motis import -c /var/lib/motis/config.yml > /var/lib/motis/motis-import.log
chown -R motis:motis /var/lib/motis/data/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
