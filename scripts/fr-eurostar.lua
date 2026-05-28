-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- change generic rail route type to highspeed rail
    route:set_route_type(101)
end

function process_trip(trip)
    -- Use trip short name as display name
    trip:set_display_name('EST ' .. trip:get_short_name())
end
