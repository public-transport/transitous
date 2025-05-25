#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"

{% if motis_primary is not defined or not motis_primary %}

{% if motis_no_cow %}
#cp -r -p /var/lib/motis/data /var/cache/transitous/out/data
sudo -u motis cp -r -p /var/cache/transitous/out/osm/ /var/cache/transitous/out/data/ # TODO -l
{% endif %}

cd /var/cache/transitous/out/
sudo -u motis wget -N -nH --cut-dirs=1 --exclude-directories=/gtfs/data/tiles/,/gtfs/data/osr/ --mirror --no-parent -e robots=off https://api.transitous.org/gtfs/data/ || true

{% endif %}


# Exit if empty
if [ -z "$(ls -A /var/cache/transitous/out)" ]; then
    exit 0
fi

if [ -f /var/cache/transitous/out/.import-running ]; then
    echo "Import has not finished, exiting"
    exit 0
fi

{% if motis_no_cow %}
rm -r /var/lib/motis/data/
mv /var/cache/transitous/out/data /var/lib/motis/
{% else %}
cp -r -u --reflink=auto /var/cache/transitous/out/data /var/lib/motis/
{% endif %}

cp --reflink=auto /var/cache/transitous/out/config.yml /var/lib/motis/data/config.yml

chown -R motis:www-data /var/lib/motis/data/
chmod -R u+r,g+r /var/lib/motis/data/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
