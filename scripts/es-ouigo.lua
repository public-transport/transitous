-- SPDX-FileCopyrightText: Volker Krause <vkrause@kde.org>
-- SPDX-License-Identifier: AGPL-3.0-or-later

function process_trip(trip)
    trip:set_display_name(trip:get_short_name())
end
