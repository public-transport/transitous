-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    if route:get_route_type() == 100 and route:get_short_name() == "L" then
        route:set_route_type(106)
    end
    if route:get_route_type() == 100 and route:get_short_name():sub(1, 1) == "S" then
        route:set_route_type(109)
    end
end

local use_trip_short_name = {
    ["IC"] = true,
    ["L"] = true,
    ["P"] = true
}

function process_trip(trip)
    if use_trip_short_name[trip:get_route():get_short_name()] then
        trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
    end
end
