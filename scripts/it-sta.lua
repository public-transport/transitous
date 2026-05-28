-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- drop all rail services, we get those from the Trenitalia and ÖBB feeds already
    if route:get_route_type() == 2 then
        return false
    end
end
