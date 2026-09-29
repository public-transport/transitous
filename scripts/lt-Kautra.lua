-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- change generic bus type to long-distance coach
-- routes 101 to 199 are Kaunas local buses
function process_route(route)
    if route:get_route_type() == 3 and route:get_short_name() < 200 then
        route:set_route_type(COACH)
    end
-- remove duplicated/outdated routes
    if string.find(route:get_short_name(), "D" or "EL" or "FIN" or "RK") then
        return false
    end
end


