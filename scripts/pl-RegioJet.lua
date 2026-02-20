-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    if string.find(route:get_id(), "WEB/11755") then
        route:set_route_type(104) -- SLEEPER_RAIL_SERVICE in future motis
    else
        route:set_route_type(102) -- LONG_DISTANCE_TRAINS_SERVICE in future motis
    end
end

function process_trip(trip)
  trip:set_display_name(trip:get_short_name())
end
