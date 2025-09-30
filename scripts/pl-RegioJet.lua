-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    if route:get_id() == "WEB/11755" then
        route:set_clasz(4)
    else
        route:set_clasz(2)
    end
end
