-- SPDX-FileCopyrightText: Mikołaj Kuranowski <mkuranowski@gmail.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    local short_name = route:get_short_name()
    if string.find(short_name, "KTX") then
        route:set_route_type(HIGH_SPEED_RAIL_SERVICE)
    elseif string.find(short_name, "ITX") then
        route:set_route_type(LONG_DISTANCE_TRAINS_SERVICE)
    else
        route:set_route_type(INTER_REGIONAL_RAIL_SERVICE)
    end
end

function process_trip(trip)
    trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
end
