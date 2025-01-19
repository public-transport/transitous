#!/bin/bash -e
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

echo "Copying new files…"

# Exit if empty
if [ -z "$(ls -A /srv/rsync/transitous/)" ]; then
    exit 0
fi

rsync -a --progress -r /srv/rsync/transitous/ /var/lib/motis/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
