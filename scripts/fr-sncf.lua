-- SPDX-FileCopyrightText: Felix Gündling <felixguendling@gmail.com>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_trip(trip)
    local brand = trip:get_vehicle_type_short_name()
    if brand == 'LYR' then
            brand = 'TGV Lyria'
    elseif brand == 'TGVOUIGO' or brand == 'INCONNU' then
            brand = 'OUIGO'
    elseif brand == 'OUI' then
            brand = 'TGV INOUI'
    elseif brand == 'DBS' then
            brand = 'ICE'
    end
    trip:set_display_name(brand .. ' ' .. trip:get_short_name())
    if trip:get_route():get_route_type() == 101 or trip:get_route():get_route_type() == 102 then
        trip:set_compulsory_reservation(true)
    end
end

