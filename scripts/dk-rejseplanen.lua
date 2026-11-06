-- SPDX-FileCopyrightText: Jonah Brüchert <jbb@kaidan.im>
-- SPDX-License-Identifier: AGPL-3.0-or-later

local route_type = {
    {"ECE", 101},
    {"ICL", 101},
    {"RJ", 101},
    {"IC", 102},
    {"RE", 106}
}

function remove_leading_zeros(str)
  return string.format("%d", tonumber(str))
end

function is_number(str)
  return not (str == "" or str:find("%D"))
end

function process_trip(trip)
  if trip:get_route():get_agency():get_name() == 'DSB' then
    if is_number(trip:get_short_name()) then
      trip:set_display_name(trip:get_route():get_short_name() .. ' ' .. remove_leading_zeros(trip:get_short_name()))
    end
  end

  local agency = trip:get_route():get_agency():get_name();

  if trip:get_route():get_route_type() == 2 then
    if agency == "DSB Vores Tog" then
      trip:set_display_name(remove_leading_zeros(trip:get_short_name()))
    elseif agency == "Lokaltog A/S" or agency == "Midttrafik" then
      trip:set_display_name("Lokalbane " .. trip:get_route():get_short_name())
    elseif agency == "NT" then
      trip:set_display_name(trip:get_route():get_short_name())
    elseif agency == "Skånetrafiken" then
      trip:set_display_name(remove_leading_zeros(trip:get_short_name()))
    end
  end
end

function process_route(route)
  for _, v in ipairs(route_type) do
    if v[1] == route:get_short_name() then
        route:set_route_type(v[2])
      break
    end
  end

  local agency = route:get_agency():get_name();
  if route:get_route_type() == 2 then
    if agency == "Snälltåget AB" then
      route:set_route_type(105)
    end
  end
end
