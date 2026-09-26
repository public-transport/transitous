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

local location_overrides = {
	-- Hergenrath
	["S8844644"] = { 50.7090259, 6.0432282 },
	["8844644"] = { 50.7090259, 6.0432282 },
	["8844644_1"] = { 50.7090182, 6.0432049 },
	["8844644_2"] = { 50.7090338, 6.0432516 },
}

function process_location(location)
	local override_pos = location_overrides[location:get_id()]
	if override_pos ~= nil then
		local pos = location:get_pos()
		pos:set_lat(override_pos[1])
		pos:set_lng(override_pos[2])
		location:set_pos(pos)
	end
end
