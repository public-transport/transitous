-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

local route_type_map = {
    { 2, "ICE", 101 },
    { 2, "Eurostar", 101 },
    { 2, "Intercity direct", 102 },
    { 2, "Eurocity Direct", 102 },
    { 2, "Eurocity", 103 },
    { 2, "Intercity", 103 },
    { 2, "Sprinter", 106 },
}

function process_route(route)
    -- correct route type for European Sleeper
    if route:get_route_type() == 2 and route:get_agency():get_name() == "European Sleeper" then
        route:set_route_type(105)
    else
        for _,m in ipairs(route_type_map) do
            if route:get_route_type() == m[1] and route:get_short_name() == m[2] then
                route:set_route_type(m[3])
                break
            end
        end
    end
    return true
end
