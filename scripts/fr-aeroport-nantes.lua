-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_route(route)
    if route:agency_id().match(".*AEROPORT_NANTES.*") and route:short_name().match("...-...") then
        route:set_clasz(AIRPLANE)
        route:set_route_type(nil)
    end
end
