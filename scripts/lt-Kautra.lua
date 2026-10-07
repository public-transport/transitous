-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- change generic bus type to long-distance coach
-- routes 101 to 199 are Kaunas local buses
function process_route(route)
    if route:get_route_type() == 3 and route:get_short_name() < 200 then
        route:set_route_type(200)
    end
-- remove most of international routes in feed (they are duplicates of Flixbus or Lux Express coaches already included in other feeds and also it doesn't seem to have trips regularily updated)
-- basically M lines with numbers 1000 and higher (these are international) have to be skipped, please help me in this
    if string.find(route:get_short_name(), "D" or "EL" or "FIN" or "RK" or "N") or route:get_short_name() == "M-1017" then
        return false
    end
-- Druskininkai balloon
    if route:get_short_name() == "M-001" then
        route:set_route_type(1300)
    end
end

function process_location(stop)
     local pos
     pos:set_lat(54.0121915)
     pos:set_lng(23.9753437)
     if string.find(stop:get_name(), "~Balionas") then
        stop:set_pos(pos)
    end
end
