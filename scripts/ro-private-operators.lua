-- SPDX-FileCopyrightText: 2026 Jonah Brüchert <jbb@kaidan.im>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_trip(trip)
    if trip:get_route():get_short_name() and trip:get_short_name() then
        trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
    end
end
