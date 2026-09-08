-- SPDX-FileCopyrightText: Jonah Brüchert <jbb@kaidan.im>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    if route:get_route_type() == 2 then
        route:set_route_type(106)
    end
end

function process_trip(trip)
    if trip:get_route():get_route_type() == 2 or trip:get_route():get_route_type() == 106 then
        -- Use trip short name as display name
        trip:set_display_name('TER ' .. trip:get_short_name())
    end
end
