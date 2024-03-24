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

if len(sys.argv) < 2:
    print("Argument run-reason is missing.")
    print("Must be one of timer, merge-request")
    sys.exit(1)

run_reason = sys.argv[1]
feed_dir = Path("feeds/")
repo = "public-transport/transitous"


def create_feed_error_issue(feed: str, details: str, github_token: str) -> None:
    issue_title = f"Error fetching '{feed}'"

    # Check if an error issue already exists
    response = requests.get(
        "https://api.github.com/search/issues",
        headers={"Authorization": f"Bearer {github_token}"},
        params={"q": f"repo:{repo} is:issue {issue_title}"},
    )

    if response.status_code < 200 or response.status_code >= 300:
        print(f"Error searching for existing issue for {feed}")
        print(response.json())
        return

    if response.json()["total_count"] > 0:
        if issue["title"] == issue_title:
            # Update the issue with the new error
            issue_number = response.json()["items"][0]["number"]
            requests.patch(
                f"https://api.github.com/repos/{repo}/issues/{issue_number}",
                headers={"Authorization": f"Bearer {github_token}"},
                json={"body": f"{issue['body']}\n\n```{details}```"},
            )
            print(f"Updated error issue for {feed}")
            return

    # Create an issue on the repository
    response = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={"Authorization": f"Bearer {github_token}"},
        json={
            "title": issue_title,
            "body": f"Error fetching {feed}\n\n```{details}```",
            "labels": ["import-issue"],
        },
    )

    if response.status_code < 200 or response.status_code >= 300:
        print(f"Error creating issue for {feed}")
        print(response.json())
        return

    print(f"Created error issue for {feed}")


def do_fetch(feed: str):
    try:
        subprocess.check_call(["./src/fetch.py", feed])
    except:
        print(f"Error fetching {feed}")
        if "GITHUB_TOKEN" in os.environ:
            details = subprocess.check_output(
                ["./src/fetch.py", feed], stderr=subprocess.STDOUT
            ).decode()
            create_feed_error_issue(feed, details, os.environ["GITHUB_TOKEN"])


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
            f
            for f in changed_files
            if Path(f).exists() and f.startswith("feeds/") and f.endswith(".json")
        ]

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=multiprocessing.cpu_count()
        ) as executor:
            for feed in changed_feeds:
                executor.submit(do_fetch, feed)
