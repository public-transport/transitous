-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- source route type, route type name prefix, MOTIS class, target route type, display name prefix
local route_type_map = {
    { 2, "Intercity direct", 102, "ICD" },
    { 2, "Intercity", 103, nil },
    { 2, "Sprinter", 106, nil },
    { 2, "Sneltrein", 106, nil },
    { 2, "Stoptrein", 106, nil },
    { 2, "Nightjet", 105, "NJ" },
    { 2, "Eurocity Direct", 102, "ECD" },
    { 2, "EuroCity", 102, "ECC" },
    { 2, "ICE", 101, "ICE" },
    { 2, "Eurostar", 101, "EST" },
}

function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == m[1] and route:get_short_name():sub(1, #m[2]):lower() == m[2]:lower() then
            route:set_route_type(m[3])
            break
        end
    end
end

function process_trip(trip)
    local route = trip:get_route()
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == m[3] and route:get_short_name():sub(1, #m[2]) == m[2] and m[4] then
            trip:set_display_name(m[4] .. " " .. trip:get_short_name())
        end
    end
end
