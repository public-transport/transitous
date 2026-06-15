-- SPDX-FileCopyrightText: applecuckoo <nufjoysb@duck.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- skip Te Huia in favour of AT feed
    if route:get_short_name() == "TE_HUIA" then
        return false
    end
end
