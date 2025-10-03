-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_trip(trip)
    -- dispaly names for international SBB EC/IC trips and DB ICEs
    if trip:get_route():get_short_name() == "EC" or trip:get_route():get_short_name() == "IC" or trip:get_route():get_short_name() == "ICE" then
        trip:set_display_name(trip:get_route():get_short_name() .. ' ' .. trip:get_short_name())
    end

    -- display names for SNCF trips
    if trip:get_route():get_agency():get_id() == "87_LEX" then
        if trip:get_route():get_route_type() == 101 then
            trip:set_display_name("TGV " .. trip:get_short_name())
        end
        if trip:get_route():get_route_type() == 102 then
            trip:set_display_name("IC " .. trip:get_short_name())
        end
    end
end
