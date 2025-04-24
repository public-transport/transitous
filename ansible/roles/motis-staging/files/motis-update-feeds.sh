#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"

# Exit if empty
if [ -z "$(ls -A /var/cache/transitous/out)" ]; then
    exit 0
fi

if [ -f /var/cache/transitous/out/.import-running ]; then
    echo "Import has not finished, exiting"
    exit 0
fi

cd /var/lib/motis
touch /var/lib/motis/import-running
wget --mirror -l 1 --no-parent --no-directories --accept gtfs.zip --accept config.yml -e robots=off https://api.transitous.org/gtfs/
/opt/motis/motis import -c /var/lib/motis/config.yml > /var/lib/motis/motis-import.log
cp -r -u --reflink=auto /var/cache/transitous/out/data /var/lib/motis/
cp --reflink=auto /var/cache/transitous/out/config.yml /var/lib/motis/data/config.yml
chown -R motis:motis /var/lib/motis/data/
rm /var/lib/motis/import-running

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
