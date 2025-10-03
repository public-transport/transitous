-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
	route:set_clasz(SUBURBAN)
end

function process_trip(trip)
  trip:set_display_name("S1")
end
