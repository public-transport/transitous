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

if len(sys.argv) < 2:
    print("Argument run-reason is missing.")
    print("Must be one of timer, merge-request")
    sys.exit(1)

run_reason = sys.argv[1]
feed_dir = Path("feeds/")

def do_fetch(feed: str):
    try:
        subprocess.check_call(["./src/fetch.py", feed])
    except:
        print(f"Error fetching {feed}")
        # TODO: create an issue on the repository

match run_reason:
    case "timer":
        json_files = list(feed_dir.glob("*.json"))

        max_workers = multiprocessing.cpu_count()
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for index, feed in enumerate(json_files):
                print(f'PROGRESS: Processing file {index+1} of {len(json_files)} | {index/len(json_files)*100:.1f}% done...')
                sys.stdout.flush()
                executor.submit(do_fetch, feed)

        subprocess.check_call(["./src/garbage-collect.py"])
    case "merge-request":
        # Silence warnings about different ownerships inside and outside of the
        # container on actions
        subprocess.check_call(
            ["git", "config", "--global",
             "--add", "safe.directory", os.getcwd()])

        # Find all files that were changed in the latest commit
        changed_files = subprocess.check_output(
            ["git", "diff", "--name-only", "origin/main", "HEAD"]) \
            .decode().splitlines()

        changed_feeds = [f for f in changed_files if Path(f).exists() and
                         f.startswith("feeds/") and f.endswith(".json")]

        max_workers = 4
        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            for index, feed in enumerate(changed_feeds):
                print(f'PROGRESS: Processing file {index+1} of {len(changed_feeds)} | {index/len(changed_feeds)*100:.1f}% done...')
                sys.stdout.flush()
                executor.submit(do_fetch, feed)
