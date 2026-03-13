-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- source route type, route type name prefix, target route type
local route_type_map = {
    { 2, "ALVIA", 101 },
    { 2, "AVANT", 101 },
    { 2, "AVE", 101 },
    { 2, "AVE INT", 101 },
    { 2, "AVLO", 101 },
    { 2, "EUROMED", 101 },
    { 2, "Intercity", 102 },
    { 2, "MD", 103 },
    { 2, "REGIONAL", 106 },
    { 2, "REG.EXP", 106 },
    { 2, "PROXIMDAD", 106 },
    { 2, "TRENCELTA", 103 },
}

function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == m[1] and route:get_short_name():sub(1, #m[2]) == m[2] then
            route:set_route_type(m[3])
            break
        end
    end
    route:set_text_color(0)
end

function process_trip(trip)
    trip:set_display_name(trip:get_route():get_short_name() .. ' ' .. trip:get_short_name())
end
