-- SPDX-FileCopyrightText: Traines
-- SPDX-License-Identifier: AGPL-3.0-or-later

local route_type_map = {
    ["Sudbury - White River"] = 106,
    ["The Pas - Churchill"] = 106,
}

function process_route(route)
    if route:get_route_type() ~= 2 then
        return
    end

    route:set_route_type(route_type_map[route:get_long_name()] or 102)
end
