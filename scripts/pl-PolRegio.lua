-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_trip(trip)
	if trip:get_route():get_short_name() == "REG" then
		trip:set_display_name("R " .. trip:get_short_name())
	else
		trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
	end
end

function process_route(route)
	if route:get_short_name() == "REG" then
		route:set_route_type(106) --REGIONAL_RAIL_SERVICE in future motis
	elseif route:get_short_name() == "IR" then
		route:set_route_type(100) --RAILWAY_SERVICE in future motis
	elseif route:get_short_name() == "ZKA REG" then
		route:set_route_type(714) --RAIL_REPLACEMENT_BUS_SERVICE in future motis
	end
end
