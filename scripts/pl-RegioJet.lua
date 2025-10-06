-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
    if string.find(route:get_id(), "WEB/11755") then
        route:set_clasz(NIGHT_RAIL)
    else
        route:set_clasz(LONG_DISTANCE)
    end
end

function process_trip(trip)
  trip:set_display_name(trip:get_short_name())
end
