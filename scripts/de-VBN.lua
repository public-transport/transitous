-- SPDX-FileCopyrightText: Felix Gündling <felixguendling@gmail.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

local colors = require 'scripts.de-delfi-colors'

function process_route(route)
  local agency_name = route:get_agency():get_name()
  local route_name = route:get_short_name()
	-- remove spaces from route name for matching
	route_name = route_name:gsub("%s+", "")
	local original_route_color = route:get_color()
	local original_route_text_color = route:get_text_color()
  if (original_route_color == 0 or original_route_text_color == 0) and colors[agency_name] and colors[agency_name][route_name] then
    local c = colors[agency_name][route_name]
    route:set_color(c.color)
    route:set_text_color(c.text_color)
  end
end
