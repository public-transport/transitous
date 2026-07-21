-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    if route:get_id() == "BV" or route:get_id() == "MBV" then
        route:set_route_type(102)
    elseif route:get_id() == "PV" or route:get_id() == "KPV" then
        route:set_route_type(106)
    elseif route:get_id() == "A" then
        route:set_route_type(714)
    end
end

function process_trip(trip)
    trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
end
