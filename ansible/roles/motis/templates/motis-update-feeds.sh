#!/bin/bash -xe
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

{% if no_cow is defined and no_cow %}
cp -rp /var/cache/transitous/out/data/ /var/lib/motis/data.tmp/
rm -rf /var/lib/motis/data.bak/
systemctl --no-ask-password stop motis.service

mv /var/lib/motis/data/ /var/lib/motis/data.bak/
mv /var/lib/motis/data.tmp/ /var/lib/motis/data/
{% else %}
cp -r -u --reflink=auto /var/cache/transitous/out/data /var/lib/motis/
{% endif %}

cp --reflink=auto /var/cache/transitous/out/config.yml /var/lib/motis/data/config.yml

chown -R motis:motis /var/lib/motis/data/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
