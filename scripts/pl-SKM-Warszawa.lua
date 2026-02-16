-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
  	route:set_route_type(109) -- SUBURBAN_RAILWAY_SERVICE in future motis
	route:set_clasz(SUBURBAN)
end
