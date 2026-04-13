-- SPDX-FileCopyrightText: Felix Gündling <felixguendling@gmail.com>
-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- route short name, target route type
local route_type_map = {
    { "FR", 101 },
    { "FA", 101 },
    { "FB", 102 },
    { "IC", 102 },
    { "EC", 102 },
    { "ICN", 105 },
    { "ECN", 105 },
    { "RV", 106 },
    { "REG", 106 },
}

function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == 100 and route:get_short_name() == m[1] then
            route:set_route_type(m[2])
            break
        end
    end
end

function process_trip(trip)
    -- example: IT::VehicleJourney:railTRENITALIA:680083_0_68-9330-27F-0083_68-9330-27F-0083
    -- where 9330 is the train number
    local id = trip:get_id()
    local train_nr = id:match("railTRENITALIA:[^-]+%-(%d+)%-") or ''
    trip:set_display_name(trip:get_route():get_short_name() .. ' ' .. train_nr)
end
