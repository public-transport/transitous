-- Unfortunately, the feed lumps routes together by franchise, making fine-grained type assignment impossible for the time being
local route_type_map = {
    -- Caledonian Sleeper
    ["CS"] = { route_type = 105 },
    -- Chiltern Railways
    ["CH"] = { route_type = 106 },
    -- CrossCountry
    ["XC"] = { route_type = 102 },
    -- Gatwick Express
    ["GX"] = { route_type = 2 },
    -- Grand Central
    ["GC"] = { route_type = 102 },
    -- Great Northern
    ["GN"] = { route_type = 106 },
    -- Greater Anglia
    ["LE"] = { route_type = 106 },
    -- Heathrow Express
    ["HX"] = { route_type = 2 },
    -- Hull Trains
    ["HT"] = { route_type = 102 },
    -- Island Line
    ["IL"] = { route_type = 106 },
    -- Lumo
    ["LD"] = { route_type = 102 },
    -- Northern
    ["NT"] = { route_type = 106 },
    -- ScotRail is not classified because it operates intercity and (fast) regional trains
    -- ["=SR"] = { route_type = 106 },
    -- Southeastern (might also be classified as fast regional)
    ["SE"] = { route_type = 106 },
    -- Southern
    ["SN"] = { route_type = 106 },
    -- Stansted Express
    ["SX"] = { route_type = 2 },
    -- Thameslink
    ["TL"] = { route_type = 109 },
    -- c2c
    ["CC"] = { route_type = 106 },
    -- Avanti West Coast
    ["VT"] = { route_type = 102 },
    -- East Midlands Railway (also runs some intercity routes)
    ["EM"] = { route_type = 2 },
    -- Great Western Railway (also runs some (fast) regional routes and the "Night Riviera" sleeper train)
    ["GW"] = { route_type = 102 },
    -- LNER
    ["GR"] = { route_type = 102 },
    -- London and Northwestern Railway
    ["LN"] = { route_type = 2 },
    -- South Western Railway
    ["SW"] = { route_type = 106 },
    -- TransPennie Express
    ["TP"] = { route_type = 2 },
    -- Transport for Wales
    ["AW"] = { route_type = 106 },
    -- West Midlands Railway
    ["WM"] = { route_type = 106 },
}

function process_route(route)
    local route_id = route:get_id()
    if route_type_map[route_id] then
        local route_type = route_type_map[route_id].route_type
        route:set_route_type(route_type)
    end
end
