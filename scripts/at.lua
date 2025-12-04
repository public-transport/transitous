-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

-- Mapping table for Austrian route types
-- Format: { source route type, route name prefix, MOTIS class, target route type }
local route_type_map = {
    { 2, "RJX", HIGHSPEED_RAIL, 101 }, -- Railjet Express (high-speed rail)
    { 2, "RJ", HIGHSPEED_RAIL, 101 },  -- Railjet (high-speed rail)
    { 2, "ICE", HIGHSPEED_RAIL, 101 }, -- InterCity Express (high-speed rail)
    { 2, "IC", LONG_DISTANCE, 102 },   -- InterCity (long-distance rail)
    { 2, "NJ", NIGHT_RAIL, 105 },      -- Nightjet (night rail)
    { 2, "EN", NIGHT_RAIL, 105 },      -- EuroNight (night rail)
    { 2, "ECB", LONG_DISTANCE, 102 },  -- EuroCity Bus (long-distance)
    { 2, "EC", LONG_DISTANCE, 102 },   -- EuroCity (long-distance rail)
    { 2, "REX", REGIONAL_FAST_RAIL, 106 }, -- Regional Express (fast regional rail)
    { 2, "CJX", REGIONAL_FAST_RAIL, 106 }, -- CityJet Express (fast regional rail)
    { 2, "D", LONG_DISTANCE, 102 },    -- D-train (long-distance rail)
    { 2, "R", REGIONAL_RAIL, 106 },    -- Regional train
    { 2, "S", SUBURBAN, 109 },         -- Suburban train (S-Bahn)
    { 3, "ICBus", COACH, 200 },        -- InterCity Bus
}

-- Function to process a route and assign the correct MOTIS class and target type
function process_route(route)
    for _,m in ipairs(route_type_map) do
        if route:get_route_type() == m[1] and route:get_short_name():sub(1, #m[2]) == m[2] then
            route:set_clasz(m[3])       -- Set the MOTIS class (e.g., high-speed, regional, night rail)
            route:set_route_type(m[4])  -- Set the target route type code
            break
        end
    end
end
