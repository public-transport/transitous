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


def data_zielona_gora_latest_resource(source: HttpSource) -> HttpSource:
    from bs4 import BeautifulSoup

    html = requests.get(source.url).text
    

    soup = BeautifulSoup(html, "lxml")
    gtfs_link = next((a["href"] for a in soup.find_all("a") if "GTFS" in a.get_text()), None)

    base_url = source.url.rsplit("/", 1)[0]
    source.url = f"{base_url}/{gtfs_link}"

    return source


def data_slupsk_latest_resource(source: HttpSource) -> HttpSource:
    from bs4 import BeautifulSoup

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    } # user-agent is necessary to avoid 403 Forbidden

    html = requests.get(source.url, headers=headers).text

    soup = BeautifulSoup(html, "lxml")
    gtfs_link = soup.find("a", href=lambda x: x and x.endswith(".zip"))["href"]

    base_url = source.url.rsplit("/", 1)[0]
    source.url = f"{base_url}/{gtfs_link}"

    return source


def data_tasmania_latest_resource(source: HttpSource) -> HttpSource:
    from bs4 import BeautifulSoup
    
    html = requests.get(source.url).text

    soup = BeautifulSoup(html, "lxml")
    source.url = soup.find("a", href=lambda x: x and x.endswith(".zip"))["href"]

    return source


def data_kaposvar_latest_resource(source: HttpSource) -> HttpSource:
    import re
    from bs4 import BeautifulSoup
    from urllib.parse import quote, urlsplit

    split_source_url = urlsplit(source.url)

    page_html = requests.get(source.url).text
    page_html_parsed = BeautifulSoup(page_html, "lxml")

    contains_word_gtfs = re.compile(r".*GTFS.*", re.IGNORECASE)
    url_path_tag = page_html_parsed.find("a", string=contains_word_gtfs)
    assert url_path_tag

    url_path = url_path_tag["href"]
    url_path_safe = quote(url_path)

    source.url = f"{split_source_url.scheme}://{split_source_url.netloc}{url_path_safe}"
    return source


def data_hodmezovasarhely_latest_resource(source: HttpSource) -> HttpSource:
    import re
    from bs4 import BeautifulSoup

    page_html = requests.get(source.url).text
    page_html_parsed = BeautifulSoup(page_html, "lxml")

    contains_word_gtfs = re.compile(r".*GTFS.*", re.IGNORECASE)
    url_paragraph_label = page_html_parsed.find("span", string=contains_word_gtfs)
    assert url_paragraph_label

    url_paragraph = url_paragraph_label.parent.parent
    return url_paragraph["href"]


def data_metroporto_latest_resource(source: HttpSource) -> HttpSource:
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    headers = {
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        )
    }

    html = requests.get(source.url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    li = soup.find("li", class_=lambda c: c and "last zip" in c)
    if li is None:
        raise ValueError("Could not find the latest GTFS link on Metro do Porto page")

    a_tag = li.find("a")
    if a_tag is None or "href" not in a_tag.attrs:
        raise ValueError("No <a> tag with href found inside the <li>")

    gtfs_url = urljoin(source.url, a_tag["href"])

    source.url = gtfs_url
    return source


def chile_dtp_downloader(source: HttpSource) -> HttpSource:
    import re
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    """
    Fetches the current GTFS feed link from the DTPM Chile website.

    Steps:
    1. Downloads the GTFS vigente page.
    2. Looks for links that match the pattern: GTFS_YYYYMMDD*.zip
       - If found, picks the feed with the most recent date.
    3. If no date-based links are found, falls back to collecting all
       GTFS .zip links and returns the lexicographically largest one.
    4. Returns None if no GTFS links are found at all.
    """
    response = requests.get(source.url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    pattern = re.compile(r"GTFS_(\d{8})[^/]*\.zip")

    dated_feeds = []
    all_gtfs_feeds = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "gtfs" in href.lower() and href.lower().endswith(".zip"):
            full_url = urljoin(source.url, href)
            all_gtfs_feeds.append(full_url)

            match = pattern.search(href)
            if match:
                date_str = match.group(1)
                dated_feeds.append((int(date_str), full_url))

    # Case 1: Found valid date-based feeds → choose latest
    if dated_feeds:
        dated_feeds.sort(key=lambda x: x[0], reverse=True)
        source.url = dated_feeds[0][1]
        return source

    # Case 2: Fallback → lexicographically largest GTFS link
    if not all_gtfs_feeds:
        raise ValueError("No GTFS files found!")

    source.url = max(all_gtfs_feeds)
    return source
