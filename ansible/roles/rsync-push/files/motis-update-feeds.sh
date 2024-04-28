#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"

# Exit if empty
if [ -z "$(ls -A /srv/rsync/transitous/)" ]; then
    exit 0
fi

rm /var/lib/motis/data/nigiri/ -rf
rsync --progress -r -u /srv/rsync/transitous/ /var/lib/motis/
chown motis:motis -R /var/lib/motis/data/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
