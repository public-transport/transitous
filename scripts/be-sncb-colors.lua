-- SPDX-FileCopyrightText: Dan Cojocaru <dan@dcdev.ro>
-- SPDX-License-Identifier: AGPL-3.0-or-later

local colors = {
	-- S Train Brussels
	-- Source: https://www.belgiantrain.be/-/media/files/pdf/s-train/map-s-train-0389-brussels-nl-dec-2025.ashx
	["S1"] = { color = 0x006033, text_color = 0xffffff },
	["S2"] = { color = 0xf26222, text_color = 0xffffff },
	["S3"] = { color = 0x222875, text_color = 0xffffff },
	["S4"] = { color = 0xcc2127, text_color = 0xffffff },
	["S5"] = { color = 0xffcd06, text_color = 0xffffff },
	["S7"] = { color = 0x571759, text_color = 0xffffff },
	["S8"] = { color = 0x0096cc, text_color = 0xffffff },
	["S9"] = { color = 0x67bd45, text_color = 0xffffff },
	["S10"] = { color = 0x231f20, text_color = 0xffffff },
	["S19"] = { color = 0xf06da8, text_color = 0xffffff },
	["S20"] = { color = 0x009696, text_color = 0xffffff },
	-- S Trein Antwerpen
	-- Source: https://www.belgiantrain.be/-/media/files/pdf/s-train/map-s-train-0434-antwerp-nl-dec-2025.ashx
	["S32"] = { color = 0xf16224, text_color = 0xffffff },
	["S33"] = { color = 0x222875, text_color = 0xffffff },
	["S34"] = { color = 0xcc2127, text_color = 0xffffff },
	["S35"] = { color = 0x0391cc, text_color = 0xffffff },
	-- Train S Liège
	-- Source: https://www.belgiantrain.be/-/media/files/pdf/s-train/map-s-train-0432-liege-fr-dec-2025.ashx
	["S41"] = { color = 0x016535, text_color = 0xffffff },
	["S42"] = { color = 0xed5909, text_color = 0xffffff },
	["S43"] = { color = 0x2b267e, text_color = 0xffffff },
	["S44"] = { color = 0xc72a1e, text_color = 0xffffff },
	-- S Trein Gent
	-- Source: https://www.belgiantrain.be/-/media/files/pdf/s-train/map-s-train-0394-gent-nl-dec-2025.ashx
	["S51"] = { color = 0x006033, text_color = 0xffffff },
	["S52"] = { color = 0xf26222, text_color = 0xffffff },
	["S53"] = { color = 0x222875, text_color = 0xffffff },
	-- Train S Charleroi
	-- Source: https://www.belgiantrain.be/-/media/files/pdf/s-train/map-s-train-0433-charleroi-fr-dec-2025.ashx
	["S61"] = { color = 0x036436, text_color = 0xffffff },
	["S62"] = { color = 0xed5a08, text_color = 0xffffff },
	["S63"] = { color = 0x2b267d, text_color = 0xffffff },
	["S64"] = { color = 0xc8291f, text_color = 0xffffff },
}
return colors
