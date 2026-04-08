-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- change generic bus type to long-distance coach
function process_route(route)
    if route:get_route_type() == 3 then
        route:set_route_type(200)
  end
end
