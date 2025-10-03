-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_trip(trip)
	if trip:get_route():get_short_name() == "REG" then
		trip:set_display_name("R " .. trip:get_short_name())
	else
		trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
	end
end

function process_route(route)
	if route:get_short_name() == "REG" then
		route:set_clasz(REGIONAL_RAIL)
	elseif route:get_short_name() == "IR" then
		route:set_clasz(REGIONAL_FAST_RAIL)
	elseif route:get_short_name() == "ZKA REG" then
		route:set_clasz(BUS)
		route:set_route_type(714) -- rail replacement bus
	end
end
