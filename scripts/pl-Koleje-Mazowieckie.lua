-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    if route:get_id() == "ZL" then
        route:set_route_type(700) --BUS_SERVICE in future motis
	elseif string.find(route:get_id(), "Z") then
		route:set_route_type(714) --RAIL_REPLACEMENT_BUS_SERVICE in future motis
	elseif string.find(route:get_id(), "RE") then
		route:set_route_type(100) --RAILWAY_SERVICE in future motis
	else
		route:set_route_type(106) --REGIONAL_RAIL_SERVICE in future motis
	end
	return true
end
