-- SPDX-FileCopyrightText: ExoSkye <exoskye@tuta.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

local route_type_map = {
    -- Map to fix up the various rail transport routes in Bangkok, since many are incorrectly set as trams or as subway

    -- BTS Lines
    ["Sukhumvit"] = 109,
    ["Silom"] = 109,
    ["Gold"] = 109,

    -- MRT Lines
    ["Blue"] = 402,
    ["Purple"] = 109,
    ["Pink"] = 109,
    ["Yellow"] = 109,

    -- SRTET lines
    ["Red"] = 106,
    ["ARL"] = 106
}

local srt_route_type_map = {
    -- Map to fix the type of services based on SRT's own service designations (Local, Ordinary, Express, Special Express etc)
    -- Complete with the spelling mistakes present in the GTFS source material!
    ["Normal"] = 106,
    ["Specail City"] = 106,
    ["City"] = 106,
    ["WongwianYai - MahaChai Line"] = 106, -- Not sure why these are denoted differently, they are commuter train on ttsview
    ["BanLaem - MaeKlong Line"] = 106,
    ["Rapid"] = 106,
    ["Special Express"] = 102,
    ["Express"] = 102
}

local srt_route_number_type_map = {
    -- Individual overrides for SRT trains that have weird wrong descriptions
    -- Both of these are "Normal 3" trains in the source material, but on ttsview.railway.co.th are listed as "Special"
    ["997"] = 102,
    ["998"] = 102
}

local delete_map = {
    -- Map for known innaccurate timetables - cursory investigation showed this bus flying at an acceptable(tm) high speed over
    -- Bangkok, so very likely inaccurate since last I checked, buses can't fly. Delete an entry if the corresponding GTFS route for this bus gets fixed
    ["1-8 (59)"] = true,
    ["3-50 (195)"] = true,
    ["1-37 (27)"] = true,
}

function process_route(route)
    if route:get_agency():get_id() == "SRT" then 
        local override_entry = srt_route_number_type_map[route:get_short_name()]

        if override_entry then
            route:set_route_type(override_entry)
        else
            for search_term,route_type in ipairs(srt_route_type_map) do
                if string.find(route:get_long_name(), search_term) then
                    route:set_route_type(route_type)
                    break
                end
            end
        end
    else
        local type_entry = route_type_map[route:get_short_name()]

        if type_entry then
            route:set_route_type(type_entry)
        end
    end

    local delete_entry = delete_map[route:get_short_name()]

    if delete_entry then
        return false
    end

    return true
end
