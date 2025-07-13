# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#
# Functions in here can be called from region json files in order to
# add some dynamic information to the metadata, such as short-lived tokens.
#

from metadata import HttpSource
from datetime import datetime

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


def data_public_lu_latest_resource(
        source: HttpSource) -> HttpSource:
    api = requests.get(source.url).json()
    res = sorted(api["resources"],
                 key=lambda res: datetime.fromisoformat(res["last_modified"]),
                 reverse=True)
    source.url = res[0]["latest"]
    return source


def delhi_gov_in_csrf(source: HttpSource) -> HttpSource:
    from bs4 import BeautifulSoup
    html = requests.get(source.url).text
    element = BeautifulSoup(html, "lxml").find(attrs = {"name": "csrfmiddlewaretoken"})
    csrftoken = element["value"]
    source.options.headers["Cookie"] = f"csrftoken={csrftoken}"
    source.options.request_body = f"csrfmiddlewaretoken={csrftoken}"
    return source
