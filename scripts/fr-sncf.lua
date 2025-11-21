-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
  if route:get_short_name() == "121A" or "591A" or "180A" or "560B" or "552A" or "723A" or "722A" then  -- ICs with or without compulsory reservation
    route:set_route_type(102)
    route:set_clasz(LONG_DISTANCE)
  elseif route:get_id() == "OCESN-87141002-87722025" or "FR:Line::d1189a05-48e1-477d-9b3c-f8ac8cb0397b:" -- missing ICs and Ouigo TCs from above ('INCONNU')
    route:set_route_type(102)
    route:set_clasz(LONG_DISTANCE)
  elseif string.find(route:get_short_name(), "P" or "C" or "L" or "F") then
    route:set_route_type(106)
    route:set_clasz(REGIONAL_RAIL)
  elseif string.find(route:get_short_name(), "K" or "D" or "S") then
    route:set_route_type(106)
    route:set_clasz(REGIONAL_FAST_RAIL)

    
    route:set_route_type(714) -- rail replacement bus
    route:set_clasz(BUS)

  elseif route:get_short_name() == "" then
    route:set_route_type(102)
    route:set_clasz(NIGHT_RAIL)
  else
    route:set_route_type(101)
    route:set_clasz(HIGHSPEED_RAIL)
  end
end

function process_trip(trip)
  trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
end
