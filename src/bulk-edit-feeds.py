#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import sys
import json

region = None

with open(sys.argv[1], "r") as f:
	region = json.load(f)
	for source in region["sources"]:
		# Add migrations here
		if "http-headers" in source:
			source["options"] = {}
			source["options"]["headers"] = source["http-headers"]
			source.pop("http-headers", None)

		if "options" in source:
			source["http-options"] = source["options"]
			source.pop("options", None)

		if "proxy" in source:
			source.pop("proxy", None)
		if "use-origin" in source:
			source.pop("use-origin", None)

with open(sys.argv[1], "w") as out:
	json.dump(region, out, indent=4, ensure_ascii=False)
	out.write("\n")
