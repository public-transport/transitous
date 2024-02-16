#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess
import time
import sys


def run_motis_import() -> bool:
    p = subprocess.Popen(["motis", "--import.require_successful", "1"],
                         stderr=subprocess.PIPE)

    for line in iter(p.stderr.readline, ""):
        if p.poll():
            return False

        sys.stdout.buffer.write(line)
        if b"system boot finished" in line:
            p.terminate()
            return True
        else:
            time.sleep(1)


if __name__ == "__main__":
    if run_motis_import():
        sys.exit(0)
    else:
        sys.exit(1)
