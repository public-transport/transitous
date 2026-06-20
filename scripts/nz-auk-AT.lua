-- SPDX-FileCopyrightText: applecuckoo <nufjoysb@duck.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- set all routes with the RB (Rail Bus) prefix as rail replacement buses
    if string.find(route:get_short_name(), "RB") then
        route:set_route_type(714) -- rail replacement bus
    end
end
