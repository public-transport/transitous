# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
import os
import base64
import subprocess

AGE_SENTINEL = "AGE-ENCRYPTED:"

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def decrypt_if_necessary(val):
    if not val.startswith(AGE_SENTINEL):
        return val

    encrypted_bytes = base64.b64decode(val.replace(AGE_SENTINEL, ""))

    process = subprocess.Popen(
        ['age', '--decrypt', '-i', os.environ['TRANSITOUS_FEED_PROXY_KEY_FILE']],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = process.communicate(input=encrypted_bytes)

    if process.returncode != 0:
        print(f"Feed API key decryption failed (this is expected on PRs from forks): {stderr.decode()}")
        return ""

    return stdout.decode('utf-8')
