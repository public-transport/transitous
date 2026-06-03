-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_trip(trip)
    trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
end
