-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
	route:set_route_type(106) --REGIONAL_RAIL_SERVICE in future motis
	route:set_clasz(REGIONAL_RAIL)
end