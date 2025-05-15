#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"

{% if not motis_primary %}

cd /var/cache/transitous/out/
sudo -u motis wget --mirror --no-parent -e robots=off https://api.transitous.org/gtfs/data/ || true

{% endif %}


# Exit if empty
if [ -z "$(ls -A /var/cache/transitous/out)" ]; then
    exit 0
fi

if [ -f /var/cache/transitous/out/.import-running ]; then
    echo "Import has not finished, exiting"
    exit 0
fi

cp -r -u --reflink=auto /var/cache/transitous/out/data /var/lib/motis/
cp --reflink=auto /var/cache/transitous/out/config.yml /var/lib/motis/data/config.yml

chown -R www-data:www-data /var/lib/motis/data/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
