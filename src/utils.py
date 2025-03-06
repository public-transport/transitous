# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys

european_iso_codes = ['al', 'ad', 'at', 'be', 'ba', 'bg', 'hr', 'cy', 'cz', 'dk', 'ee', 'fi', 'fr', 'de', 'gr',
                              'hu', 'is', 'ie', 'xk', 'lv', 'li', 'lt', 'lu', 'mt', 'md', 'mc', 'nl', 'mk', 'pl', 'pt',
                              'ro', 'sm', 'rs', 'sk', 'si', 'es', 'se', 'ch', 'tr', 'ua', 'uk', 'ax', 'fo', 'sj', 'eu']

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
