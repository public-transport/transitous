-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
  if string.find(route:get_short_name(), "ZKA") then
    route:set_route_type(714) -- rail replacement bus
    route:set_clasz(10)
  elseif route:get_short_name() == "EIP" then
    route:set_route_type(101)
    route:set_clasz(1)
  elseif route:get_short_name() == "EN" then
    route:set_route_type(102)
    route:set_clasz(4)
  else
    route:set_route_type(102)
    route:set_clasz(2)
  end
end

function process_trip(trip)
  trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
end
