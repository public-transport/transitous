#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"

# Exit if empty
cd /var/lib/motis
wget --mirror -l 1 --no-parent --no-directories --accept gtfs.zip --accept config.yml -e robots=off https://api.transitous.org/gtfs/
/opt/motis/motis import -c /var/lib/motis/config.yml > /var/lib/motis/motis-import.log

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
