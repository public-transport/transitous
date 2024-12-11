#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
import os
from pathlib import Path
import subprocess
import multiprocessing
import concurrent.futures
import requests
import json
from datetime import datetime, timezone

if len(sys.argv) < 2:
    print("Argument run-reason is missing.")
    print("Must be one of timer, merge-request")
    sys.exit(1)

run_reason = sys.argv[1]
feed_dir = Path("feeds/")
repo = "public-transport/transitous"
bot_account = "transitous-bot"


def create_feed_error_issue(feed: Path, details: str, github_token: str) -> None:
    issue_title = f"Error fetching '{feed}'"

    # Check if an error issue already exists
    response = requests.get(
        "https://api.github.com/search/issues",
        headers={"Authorization": f"Bearer {github_token}"},
        params={"q": f"repo:{repo} user:{bot_account} is:issue is:open {issue_title}"},
    )

    if response.status_code < 200 or response.status_code >= 300:
        print(f"Error searching for existing issue for {feed}")
        print(response.json())
        return

    # Get latest commit hash for the feed file
    commit_id = subprocess.check_output(
        ["git", "log", "-n", "1", "--pretty=format:%H", "--", feed]
    ).decode().strip()
    feed_permalink = f"https://github.com/{repo}/blob/{commit_id}/{feed}"

    assignees = []
    with open(feed) as f:
        maintainers = json.load(f)["maintainers"]
        assignees = [maintainer["github"] for maintainer in maintainers]

    time_string = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

    if response.json()["total_count"] > 0:
        issues = response.json()["items"]
        for issue in issues:
            if issue["title"] == issue_title:
                # Update the issue with the new error
                issue_number = issue["number"]

                issue_text = \
f"""
{issue['body']}

On **{time_string}**
```{details}```
"""
                requests.patch(
                    f"https://api.github.com/repos/{repo}/issues/{issue_number}",
                    headers={"Authorization": f"Bearer {github_token}"},
                    json={"body": issue_text},
                )
                print(f"Updated error issue for {feed}")
                return

    mentions = " ".join(map(lambda a: "@" + a, assignees))

    issue_text = \
f"""
**CC**: {mentions}

An error occured while fetching a feed from [`{feed}`]({feed_permalink}).
If the error is not temporary, please consider replacing or removing the feed.
Thanks!

Here are the logs of the error(s):
On **{time_string}**:
```{details}```
"""

    # Create an issue on the repository
    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={"Authorization": f"Bearer {github_token}"},
        json={
            "title": issue_title,
            "body": issue_text,
            "labels": ["import-issue"]
        },
    )

    if response.status_code < 200 or response.status_code >= 300:
        print(f"Error creating issue for {feed}")
        print(response.json())
        return

    print(f"Created error issue for {feed}")


def do_fetch(feed: Path):
    try:
        details = subprocess.check_output(
            ["./src/fetch.py", feed], stderr=subprocess.STDOUT
        ).decode()
        print(details)
    except subprocess.CalledProcessError as error:
        print(f"Error fetching {feed}:")
        print(error.output.decode())
        if "GITHUB_TOKEN" in os.environ:
            create_feed_error_issue(feed, error.output.decode(), os.environ["GITHUB_TOKEN"])
        else:
            print("Can't report issue, because no token is set")


match run_reason:
    case "timer":
        json_files = list(feed_dir.glob("*.json"))

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        ) as executor:
            for feed in json_files:
                executor.submit(do_fetch, feed)

        subprocess.check_call(["./src/garbage-collect.py"])
    case "merge-request":
        # Silence warnings about different ownerships inside and outside of the
        # container on actions
        subprocess.check_call(
            ["git", "config", "--global", "--add", "safe.directory", os.getcwd()]
        )

        # Find all files that were changed in the latest commit
        changed_files = (
            subprocess.check_output(
                ["git", "diff", "--name-only", "origin/main", "HEAD"]
            )
            .decode()
            .splitlines()
        )

        changed_feeds = [
            Path(f)
            for f in changed_files
            if Path(f).exists() and f.startswith("feeds/") and f.endswith(".json")
        ]

        for feed in changed_feeds:
            subprocess.check_call(["./src/fetch.py", feed])
