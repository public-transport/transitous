-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

-- source route type, route type name prefix, MOTIS class, target route type
local route_type_map = {
    { 2, "RJX", HIGHSPEED_RAIL, 101 },
    { 2, "RJ", HIGHSPEED_RAIL, 101 },
    { 2, "ICE", HIGHSPEED_RAIL, 101 },
    { 2, "IC", LONG_DISTANCE, 102 },
    { 2, "NJ", NIGHT_RAIL, 105 },
    { 2, "EN", NIGHT_RAIL, 105 },
    { 2, "ECB", LONG_DISTANCE, 102 },
    { 2, "EC", LONG_DISTANCE, 102 },
    { 2, "REX", REGIONAL_FAST_RAIL, 106 },
    { 2, "CJX", REGIONAL_FAST_RAIL, 106 },
    { 2, "D", LONG_DISTANCE, 102 },
    { 2, "R", REGIONAL_RAIL, 106 },
    { 2, "S", SUBURBAN, 109 },
    { 3, "ICBus", COACH, 200 },
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
