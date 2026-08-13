-- SPDX-FileCopyrightText: Traines <git@traines.eu>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
        if route:get_route_type() == 200 or route:get_route_type() == 205 then
                route:set_route_type(204)
        end
end
