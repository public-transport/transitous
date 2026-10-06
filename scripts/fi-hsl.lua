-- SPDX-FileCopyrightText: Taavi Väänänen <taavi@majava.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- Drop train services from this feed, we get that data from
    -- Fintraffic's rail traffic management feeds already
    if route:get_route_type() == 109 then
        return false
    end
end
