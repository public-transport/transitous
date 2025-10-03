-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
  if string.find(route:get_short_name(), "ZKA") then
    route:set_route_type(714) -- rail replacement bus
    route:set_clasz(BUS)
  elseif route:get_short_name() == "EIP" then
    route:set_route_type(101)
    route:set_clasz(HIGHSPEED_RAIL)
  elseif route:get_short_name() == "EN" then
    route:set_route_type(102)
    route:set_clasz(NIGHT_RAIL)
  else
    route:set_route_type(102)
    route:set_clasz(LONG_DISTANCE)
  end
end

function process_trip(trip)
  trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
end
