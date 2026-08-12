-- SPDX-FileCopyrightText: Traines <git@traines.eu>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_route(route)
        route:set_route_type(102)
end

function process_trip(trip)
        trip:set_compulsory_reservation(true)
        trip:set_route_type(102)
end
