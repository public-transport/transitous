#!/bin/sh
# SPDX-FileCopyrightText: 2026 Traines <git@traines.eu>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Fetches the current DB-IP IP-to-Country Lite database (CC BY 4.0, https://db-ip.com).
# nginx picks up the new file by itself through geoip2 auto_reload.

set -eu

DIR=/var/lib/GeoIP
DB="$DIR/dbip-country-lite.mmdb"
MONTH="$(date +%Y-%m)"

mkdir -p "$DIR"
curl -fsSL "https://download.db-ip.com/free/dbip-country-lite-$MONTH.mmdb.gz" | gunzip > "$DB.tmp"
mv "$DB.tmp" "$DB"
