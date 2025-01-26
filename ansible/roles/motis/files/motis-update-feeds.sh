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

rsync -a --progress -r /var/cache/transitous/out /var/lib/motis/

echo "Restarting MOTIS…"
systemctl --no-ask-password restart motis.service
