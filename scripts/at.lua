-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- source route type, route type name prefix, target route type
local route_type_map = {
    { 2, "RJX", 101 },
    { 2, "RJ", 101 },
    { 2, "ICE", 101 },
    { 2, "IC", 102 },
    { 2, "NJ", 105 },
    { 2, "EN", 105 },
    { 2, "ECB", 102 },
    { 2, "EC", 102 },
    { 2, "REX", 106 },
    { 2, "CJX", 106 },
    { 2, "D", 102 },
    { 2, "R", 106 },
    { 2, "S", 109 },
    { 3, "ICBus", 200 },
}

function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == m[1] and route:get_short_name():sub(1, #m[2]) == m[2] then
            route:set_route_type(m[3])
            break
        end
    end
end
