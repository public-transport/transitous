-- SPDX-FileCopyrightText: applecuckoo <nufjoysb@duck.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
    if route:get_id() == "RTTA_REV" or route:get_id() == "RTTA_DEF" then
        -- reject non-revenue/out-of-service trips
        return false
    elseif string.find(route:get_id(), "^8[8-9]%d%u$") then
        -- reject suburban charters
        return false
    elseif string.find(route:get_id(), "^[HNWC]H0[1-9]$") or string.find(route:get_id(), "^[HNWC]H[1-9]%d$") then
        -- reject private hire intercity
        return false
    end
end
