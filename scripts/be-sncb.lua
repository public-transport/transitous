-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

local colors = require 'scripts.be-sncb-colors'

function process_route(route)
    if route:get_route_type() == 100 and route:get_short_name() == "L" then
        route:set_route_type(106)
    end
    if route:get_route_type() == 100 and route:get_short_name():sub(1, 1) == "S" then
        route:set_route_type(109)
    end

    local route_name = route:get_short_name()
	-- remove spaces from route name for matching
	route_name = route_name:gsub("%s+", "")
	local original_route_color = route:get_color()
	local original_route_text_color = route:get_text_color()
	if (original_route_color == 0 or original_route_text_color == 0) and colors[route_name] then
		local colors = colors[route_name]
		route:set_color(colors.color)
		route:set_text_color(colors.text_color)
	end
end

local use_trip_short_name = {
    ["IC"] = true,
    ["L"] = true,
    ["P"] = true,
    ["EC"] = true,
}

function process_trip(trip)
    if use_trip_short_name[trip:get_route():get_short_name()] then
        trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
    end
end
