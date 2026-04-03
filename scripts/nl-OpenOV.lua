-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

-- source route type, route type name prefix, MOTIS class, target route type, display name prefix
local route_type_map = {
    { 2, "Intercity direct", LONG_DISTANCE, 102, "ICD" },
    { 2, "Intercity", REGIONAL_FAST_RAIL, 103, "IC" },
    { 2, "Sprinter", REGIONAL_FAST_RAIL, 106, nil },
    { 2, "Sneltrein", REGIONAL_RAIL, 106, nil },
    { 2, "Stoptrein", REGIONAL_RAIL, 106, nil },
    { 2, "Nightjet", NIGHT_RAIL, 105, "NJ" },
    { 2, "EuroCity direct", LONG_DISTANCE, 102, "ECD" },
    { 2, "EuroCity", LONG_DISTANCE, 102, "EC" },
    { 2, "ICE", HIGHSPEED_RAIL, 101, "ICE" },
    { 2, "Eurostar", HIGHSPEED_RAIL, 101, "EST" },
}

function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == m[1] and route:get_short_name():sub(1, #m[2]) == m[2] then
            route:set_clasz(m[3])
            route:set_route_type(m[4])
            break
        end
    end
end

function process_trip(trip)
    local route = trip:get_route()
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == m[4] and route:get_short_name():sub(1, #m[2]) == m[2] and m[5] then
            trip:set_display_name(m[5] .. " " .. trip:get_short_name())
        end
    end
end
