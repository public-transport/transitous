#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
import os
from pathlib import Path
import subprocess

if len(sys.argv) < 2:
    print("Argument run-reason is missing.")
    print("Must be one of timer, merge-request")
    sys.exit(1)

run_reason = sys.argv[1]
feed_dir = Path("feeds/")

match run_reason:
    case "timer":
        for feed in feed_dir.glob("*.json"):
            subprocess.check_call(["./src/fetch.py", str(feed.absolute())])
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

        changed_feeds = [f for f in changed_files if
                         f.startswith("feeds/") and f.endswith(".json")]

        for feed in changed_feeds:
            subprocess.check_call(["./src/fetch.py", feed])
