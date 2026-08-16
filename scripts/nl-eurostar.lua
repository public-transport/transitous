-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
    -- change generic rail route type to highspeed rail
    if route:get_short_name() == "Eurostar" then
        route:set_clasz(HIGHSPEED_RAIL)
        route:set_route_type(101)
    end
end

function process_trip(trip)
    -- Use trip short name as display name
    if trip:get_long_name() == "Eurostar" or trip:get_route():get_short_name() == "Eurostar" then
        trip:set_display_name('EST ' .. trip:get_short_name())
    end
end
