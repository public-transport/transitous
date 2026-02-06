-- SPDX-FileCopyrightText: Felix Gündling <felixguendling@gmail.com>
-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

-- route short name, MOTIS class, target route type
local route_type_map = {
    { "FR", HIGHSPEED_RAIL, 101 },
    { "FA", HIGHSPEED_RAIL, 101 },
    { "FB", LONG_DISTANCE, 102 },
    { "IC", LONG_DISTANCE, 102 },
    { "EC", LONG_DISTANCE, 102 },
    { "ICN", NIGHT_RAIL, 105 },
    { "ECN", NIGHT_RAIL, 105 },
    { "RV", REGIONAL_FAST_RAIL, 106 },
    { "REG", REGIONAL_RAIL, 106 },
}

function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == 100 and route:get_short_name() == m[1] then
            route:set_clasz(m[2])
            route:set_route_type(m[3])
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
