-- SPDX-FileCopyrightText: applecuckoo <nufjoysb@duck.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    -- remap Wellington Cable Car from cable car to funicular
    if route:get_id() == "9" then
        route:set_route_type(1400)
    end
end
