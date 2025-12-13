#!/usr/bin/env python3
# SPDX-FileCopyrightText: Levin Baumann <github@17d.me>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# generate_colors.py - Generate Lua table of line colors from Traewelling line-colors CSV

import sys

# Import already written scripts as modules
import generate_colors
import generate_colors_CH
import generate_colors_VBN

# Telling Python to do these sequentially.
def main():
    generate_colors.main()
    generate_colors_CH.main()
    generate_colors_VBN.main()

# Don't know what that does, but it makes it work.
if __name__ == "__main__":
    main()
