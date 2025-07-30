#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"


cd /var/cache/transitous/out/
rm .import-running || true
sudo -u motis wget --limit-rate=30m --mirror -l 1 --no-parent --no-directories --accept gtfs.zip --accept config.yml --accept .import-running -e robots=off https://api.transitous.org/gtfs/ || true
#sudo -u motis wget --limit-rate=30m --mirror -l 1 --no-parent --no-directories --accept gtfs.zip -e robots=off https://api.transitous.org/gtfs/ || true

sudo -u motis cp -r -p --reflink=auto /var/cache/transitous/out/osm/ /var/cache/transitous/out/data/
sudo -u motis /opt/motis/motis import -c /var/cache/transitous/out/config.yml > /var/cache/transitous/motis-import.log 2>&1
chown -R motis:motis /var/cache/transitous/out/data/

# Exit if empty
if [ -z "$(ls -A /var/cache/transitous/out)" ]; then
    exit 0
fi

if [ -f /var/cache/transitous/out/.import-running ]; then
    echo "Import has not finished, exiting"
    exit 0
fi

if ! grep -q tiles /var/cache/transitous/out/config.yml; then
    exit 0
fi

echo "Import done."

rm -r /var/lib/motis/data.bak/ || true
mv /var/lib/motis/data/ /var/lib/motis/data.bak/

cp -r -u --reflink=auto /var/cache/transitous/out/data /var/lib/motis/
cp --reflink=auto /var/cache/transitous/out/config.yml /var/lib/motis/data/config.yml

chown -R motis:motis /var/lib/motis/data/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
