# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#
# Functions in here can be called from region json files in order to
# add some dynamic information to the metadata, such as short-lived tokens.
#

from metadata import *

import requests


def mvo_keycloak_token(source: HttpSource) -> HttpSource:
    token = requests.post("https://user.mobilitaetsverbuende.at/auth/realms/dbp-public/protocol/openid-connect/token", data={
            "client_id": "dbp-public-ui",
            "username": "5f7xgv6ilp@ro5wy.anonbox.net",
            "password": ")#E8qE'~CqND5b#",
            "grant_type": "password",
            "scope": "openid"
        }).json()["access_token"]

    source.options.headers["Authorization"] = f"Bearer {token}"

    return source
