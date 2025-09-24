-- SPDX-FileCopyrightText: Felix Gündling <felixguendling@gmail.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function is_number(str)
  return not (str == "" or str:find("%D"))
end

function remove_leading_zeros(str)
  return string.format("%d", tonumber(str))
end

function process_trip(trip)
  if trip:get_route():get_agency():get_name() == 'DB Fernverkehr AG' and is_number(trip:get_short_name()) then
    -- Format trip_short_name=`00123` to train number 123
    if trip:get_route():get_route_type() == 101 then
      trip:set_short_name('ICE ' .. remove_leading_zeros(trip:get_short_name()))
      trip:set_display_name(trip:get_short_name())
    elseif trip:get_route():get_route_type() == 102 then
      trip:set_short_name('IC ' .. remove_leading_zeros(trip:get_short_name()))
      trip:set_display_name(trip:get_short_name())
    end
  end

  if trip:get_route():get_route_type() == 106 and is_number(trip:get_short_name()) then
    trip:set_display_name(trip:get_route():get_short_name() .. ' (' .. remove_leading_zeros(trip:get_short_name()) .. ')')
  end
end
