-- SPDX-FileCopyrightText: Jonah Brüchert <jbb@kaidan.im>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_trip(trip)
    -- Use trip short name as display name
    trip:set_display_name('TER ' .. trip:get_short_name())
end
