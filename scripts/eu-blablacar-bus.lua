-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_trip(trip)
    trip:set_display_name('BlaBlaCar Bus ' .. trip:get_short_name())
    trip:set_headsign(route:get_long_name())
end
