-- SPDX-FileCopyrightText: applecuckoo <nufjoysb@duck.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- set all routes with the name "Replacement Bus" as rail replacement buses
    if route:get_short_name() == "Replacement Bus" then
        route:set_route_type(714) -- rail replacement bus
    end
end
