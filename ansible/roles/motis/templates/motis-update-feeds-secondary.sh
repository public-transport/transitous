#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"


cd /var/cache/transitous/out/

if [ -f /var/cache/transitous/out/.import-running ]; then
    echo "Import has not finished, exiting"
    exit 0
fi

touch .import-running
mv config.yml config.bak || true

sudo -u motis wget --limit-rate=30m --mirror -l 2 --no-parent --cut-dirs=1 --no-host-directories --include-directories=gtfs,gtfs/scripts --accept gtfs.zip --accept .lua --accept config.yml --accept .import-running -e robots=off https://api.transitous.org/gtfs/ || true

# Exit if empty
if [ -z "$(ls -A /var/cache/transitous/out)" ]; then
    exit 0
fi

if ! grep -q tiles /var/cache/transitous/out/config.yml; then
    exit 0
fi

sudo -u motis sed -i 's#extend_missing_footpaths: true#extend_missing_footpaths: true\n  preprocess_max_matching_distance: 250#' config.yml
sudo -u motis sed -i 's#osr_footpath: false#osr_footpath: true#' config.yml
sudo -u motis sed -i 's#street_routing: true#street_routing:\n  elevation_data_dir: ./srtm/#' config.yml
#sudo -u motis sed -i 's#elevators: false#elevators:\n  url: https://apis.deutschebahn.com/db-api-marketplace/apis/fasta/v2/facilities\n  headers:\n    DB-Client-ID: b5d28136ffedb73474cc7c97536554df\n    DB-Api-Key: ef27b9ad8149cddb6b5e8ebb559ce245#' config.yml

sudo -u motis /opt/motis/motis import -c /var/cache/transitous/out/config.yml > /var/cache/transitous/motis-import.log 2>&1
chown -R motis:motis /var/cache/transitous/out/data/

echo "Import done."
echo "Transferring..."
rsync --bwlimit=50000 -a /var/cache/transitous/out/data/ {{ motis_target_machine }}:/var/cache/transitous/out/data.tmp/
rsync --bwlimit=50000 -a /var/cache/transitous/out/config.yml {{ motis_target_machine }}:/var/cache/transitous/out/config.yml
ssh {{ motis_target_machine }} "rm -r /var/cache/transitous/out/data.bak/ || true && mv /var/cache/transitous/out/data/ /var/cache/transitous/out/data.bak/ && cp -pr /var/cache/transitous/out/data.tmp/ /var/cache/transitous/out/data/"

echo "Restarting MOTIS…"
ssh {{ motis_target_machine }} sudo /bin/systemctl --no-ask-password start motis-update-feeds.service
rm .import-running || true
