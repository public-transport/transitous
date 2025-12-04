# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# Assignment 1 – Reengineering Task
# Mathias Kozman
# Added documentation to improve code readability and maintainability.


import sys


def eprint(*args, **kwargs):
    """
    Print a message to the standard error output (stderr).

    This helper function centralizes error printing, making it easier to
    consistently display error messages across the project.

    Parameters:
        *args: The message components to print (same as print()).
        **kwargs: Optional print() keyword arguments.

    Returns:
        None
    """
    print(*args, file=sys.stderr, **kwargs)
