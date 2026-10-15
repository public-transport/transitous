-- SPDX-FileCopyrightText: Traines
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- https://en.wikipedia.org/wiki/Rail_transport_in_China#Classes_of_service
function process_route(route)
    local prefix = string.match(route:get_short_name(), "^%a*")
    if prefix == "G" or prefix == "C" or prefix == "D" then
        route:set_route_type(HIGH_SPEED_RAIL_SERVICE)
    elseif prefix == "Z" or prefix == "T" or prefix == "K" then
        route:set_route_type(LONG_DISTANCE_TRAINS_SERVICE)
    elseif prefix == "S" then
        route:set_route_type(SUBURBAN_RAILWAY_SERVICE)
    else
        route:set_route_type(REGIONAL_RAIL_SERVICE)
    end
end
