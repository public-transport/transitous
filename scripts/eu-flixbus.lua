-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- map input route type to MOTIS clasz/output route type
local route_type_map = {
  [2] = { 102 }, -- map FlixTrains from generic rail to long distance rail
  [3] = { 200 }  -- map FlixBuses from generic bus to coach service
}

function process_route(route)
  local m = route_type_map[route:get_route_type()]
  if m then
    route:set_route_type(m[1])
  end
  return true
end
