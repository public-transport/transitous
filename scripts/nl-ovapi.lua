-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- correct route type for European Sleeper
    if route:get_route_type() == 2 and route:get_agency():get_name() == "European Sleeper" then
        route:set_route_type(105)
    end
    return true
end
