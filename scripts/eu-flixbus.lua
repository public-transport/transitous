-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

-- map input route type to MOTIS clasz/output route type
local route_type_map = {
  [2] = { LONG_DISTANCE, 102 }, -- map FlixTrains from generic rail to long distance rail
  [3] = { COACH, 200 }  -- map FlixBuses from generic bus to coach service
}

function process_route(route)
  local m = route_type_map[route:get_route_type()]
  if m then
    route:set_clasz(m[1])
    route:set_route_type(m[2])
  end
  return true
end
