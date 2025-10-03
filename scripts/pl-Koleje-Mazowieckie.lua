-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
    if route:get_id() == "ZL" then
        route:set_clasz(BUS)
        route:set_route_type(700)
	elseif string.find(route:get_id(), "Z") then
		route:set_clasz(BUS)
		route:set_route_type(714) --rail replacement bus
	elseif string.find(route:get_id(), "RE") then
		route:set_clasz(REGIONAL_FAST_RAIL)
	else
		route:set_clasz(REGIONAL_RAIL)
	end
	return true
end
