-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
  route:set_route_type(109) -- SUBURBAN_RAILWAY_SERVICE in future motis
end

function process_trip(trip)
  trip:set_display_name("S1")
end
