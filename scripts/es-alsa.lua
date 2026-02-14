-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

-- local and long-distance services are mixed in this feed, route_short_name == ALSA
-- seems to match the long-distance services
function process_route(route)
    if route:get_route_type() == 3 and route:get_short_name() == "ALSA" then
        route:set_clasz(COACH)
        route:set_route_type(200)
  end
end
