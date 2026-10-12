-- SPDX-FileCopyrightText: Felix Gündling <felixguendling@gmail.com>
-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- GTFS route short name, extended GTFS route type
local route_type_map = {
    { "FR", 101 },
    { "FA", 101 },
    { "FB", 102 },
    { "IC", 102 },
    { "EC", 102 },
    { "EXP", 102 },
    { "ICN", 105 },
    { "ECN", 105 },
    { "EN", 105 },
    { "RV", 106 },
    { "REG", 106 },
    { "MET", 109 },
    { "SFM", 109 },
}

function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == 2 and route:get_short_name() == m[1] then
            route:set_route_type(m[2])
            break
        end
    end
end
