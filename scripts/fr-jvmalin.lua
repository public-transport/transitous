-- SPDX-FileCopyrightText: Transitous Contributors
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

function process_agency(agency)
    if agency:get_name() == 'HORIZON (CHATEAUROUX)' then
      agency:set_timezone('Europe/Paris')
    end
end
