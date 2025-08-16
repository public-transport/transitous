-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
  -- map FlixTrains from generic rail to long distance rail
  -- and FlixBuses from generic bus to coach service
  if route:get_route_type() == 2 then
    route:set_clasz(2)
    route:set_route_type(102)
  elseif route:get_route_type() == 3 then
    route:set_clasz(3)
    route:set_route_type(200)
  end
  return true
end
