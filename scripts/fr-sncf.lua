-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
  if route:get_short_name() == "121A" or "591A" or "180A" or "560A" or "560B" or "560D" or "552A" or "723A" or "722A" or "434A" then  -- ICs and Nantes-Paris Ouigos TC
    route:set_route_type(102)
    route:set_clasz(LONG_DISTANCE)
  elseif route:get_short_name() == "555A" or "555B" or "555C" or "770A" or "770B" then -- ICNs
    route:set_route_type(102)
    route:set_clasz(NIGHT_RAIL) --upcoming list is so long I've divided it into trains the command applies to
  elseif route:get_id() == "OCESN-87141002-87722025" or "OCESN-87713040-87722025" or "OCESN-87142125-87722025" or "OCESN-87722025-87141002" or "OCESN-87722025-87713040" or "OCESN-87722025-87142125" -- missing Nancy-Lyon ICs ('INCONNU')
    route:set_route_type(102)
    route:set_clasz(LONG_DISTANCE)
  elseif route:get_id() == "OCESN-87391003-87471003" or "OCESN-87391102-87471003" or "OCESN-87471003-87391003" or "OCESN-87471003-87391102" or "OCESN-87471003-87547000" or "OCESN-87547000-87471003" or "FR:Line::d1189a05-48e1-477d-9b3c-f8ac8cb0397b:"  -- missing Ouigo TCs
    route:set_route_type(102)
    route:set_clasz(LONG_DISTANCE)
  elseif route:get_id() == "OCESN-87611483-87547000" or "OCESN-87671008-87547000" or "OCESN-87785006-87547000" or "OCESN-87547000-87611483" or "OCESN-87547000-87671008" or "OCESN-87547000-87785006" -- missing ICNs
    route:set_route_type(102)
    route:set_clasz(NIGHT_RAIL)
  elseif string.find(route:get_short_name(), "P" or "C" or "L" or "F" or "T") then -- actually wrong, it has to analyze only the first character of string
    route:set_route_type(106)
    route:set_clasz(REGIONAL_RAIL)
  elseif string.find(route:get_short_name(), "K" or "D" or "S") then
    route:set_route_type(106)
    route:set_clasz(REGIONAL_FAST_RAIL)
  elseif string.find(route:get_short_name(), "A" or "N" or "E") then -- bus shuttles
    route:set_route_type(700)
    route:set_clasz(BUS)
  else
    route:set_route_type(101)
    route:set_clasz(HIGHSPEED_RAIL)
  end
end

function process_trip(trip)
  if trip:get_route():get_route_type() == "106" then -- regional train with 5 or 6 digits with number starting from 4 is actually a bus
    if string.len(trip:get_headway) == 5 or 6 and
      if string.byte(trip:get_headway(), 1) == "4" then
        trip:get_route():set_route_type(714) -- rail replacement bus
        trip:get_route():set_clasz(BUS)
        trip:set_display_name("Autocar TER " .. trip:get_headway())
      end
    else
    trip:set_display_name("TER " .. trip:get_headway())
  elseif trip:get_route():get_route_type() == "102" then
    if trip:get_route():get_clasz() == "NIGHT_RAIL" then
      if string.len(trip:get_headway) == 5 then
        trip:get_route():set_route_type(714)
        trip:get_route():set_clasz(BUS)
        trip:set_display_name("Autocar ICN " .. trip:get_headway())
      else
        trip:set_display_name("ICN " .. trip:get_headway())
      end -- Ouigo filtering madness
    elseif route:get_short_name() == "434A" or route:get_id() == "OCESN-87391003-87471003" or "OCESN-87391102-87471003" or "OCESN-87471003-87391003" or "OCESN-87471003-87391102" or "OCESN-87471003-87547000" or "OCESN-87547000-87471003" or "FR:Line::d1189a05-48e1-477d-9b3c-f8ac8cb0397b:" then
      trip:set_display_name("OTC " .. trip:get_headway())
    end
  elseif route:get_id() == "FR:Line::67f8a1ee-e295-40e2-82e3-0cd94e9fd8f6:" or "FR:Line::1d86325b-2798-4309-8fd8-191eeaaeeafd:" or "FR:Line::25781E87-8F7D-4110-8EAC-A00082FF6F9C:" or "FR:Line::07bfc39f-4dfd-46ce-98c3-aad42dfa98bd:" or "FR:Line::F1B5E26F-967E-48D9-ABA8-A049ADD85807:" or "FR:Line::16687383-70D2-4ABA-A124-1AB6A45C0E60:" or "FR:Line::338660B1-35FD-4306-969D-C99969913369:" or "FR:Line::2F2D9904-8003-4160-AD06-1A68D3400380:" or "FR:Line::7FADFAB2-C52C-4C0F-A4AF-8E15C7C8C9F8:" or "FR:Line::CEF7AF34-67BB-4735-B487-128F1E5EA4FA:" or "FR:Line::EB6C44B3-0091-46B2-94A4-A3CC5B1CA889:" or "FR:Line::CEF7AF34-67BB-4735-B487-128F1E5EA4FA:" or "FR:Line::D1E5AD07-58C1-456A-B4E2-928E91061B0B:" or "FR:Line::CEF7AF34-67BB-4735-B487-128F1E5EA4FA:" or "FR:Line::7B6D24C9-C97E-4983-9E87-29A881C982D9:" or "FR:Line::eed1f4f9-faf0-4ff5-a0a9-54e6e17ca1b4:" or "OCESN-87686006-87741793" or "OCESN-87741793-87686006" or "FR:Line::CEF7AF34-67BB-4735-B487-128F1E5EA4FA:" then
    trip:set_display_name("OGV " .. trip:get_headway())
  else
    trip:set_display_name("TGV " .. trip:get_headway())
end
