# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
