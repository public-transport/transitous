-- SPDX-FileCopyrightText: Marcus Lundblad <ml@dfupdate.se>
-- SPDX-License-Identifier: AGPL-3.0-or-later

require "scripts.motis"

-- map input route type to MOTIS clasz/output route type
local agency_route_type_map = {
  ["DVVJ"] = {
    [102] = { LONG_DISTANCE, 107 } -- map DVVJ from long distance rail to tourist rail
  },
  ["Lennakatten"] = {
    [102] = { LONG_DISTANCE, 107 } -- map Lennakatten from long distance rail to tourist rail
  },
  ["TJF Smalspåret"] = {
    [102] = { LONG_DISTANCE, 107 } -- map TJF from long distance rail to tourist rail
  }
}

-- override route_short_name and route colors based on route_id
local route_id_short_name_color_map = {
  ["1275000700001"] = { "7", 0xFF999999, 0xFFFFFFFF }, -- Stockholm tram 7
  ["1275001000001"] = { "10", 0xFF0089CA, 0xFFFFFFFF }, -- Stockholm metro 10 (blue line)
  ["1275001100001"] = { "11", 0xFF0089CA, 0xFFFFFFFF }, -- Stockholm metro 11 (blue line)
  ["1275001200001"] = { "12", 0xFF669999, 0xFFFFFFFF }, -- Stockholm Nockebybanan 12
  ["1275001300001"] = { "13", 0xFFD71D24, 0xFFFFFFFF }, -- Stockholm metro 13 (red line)
  ["1275001400001"] = { "14", 0xFFD71D24, 0xFFFFFFFF }, -- Stockholm metro 14 (red line)
  ["1275001700001"] = { "17", 0xFF04A64A, 0xFFFFFFFF }, -- Stockholm metro 17 (green line)
  ["1275001800001"] = { "18", 0xFF04A64A, 0xFFFFFFFF }, -- Stockholm metro 18 (green line)
  ["1275001900001"] = { "19", 0xFF04A64A, 0xFFFFFFFF }, -- Stockholm metro 19 (green line)
  ["1275002100001"] = { "21", 0xFFB66931, 0xFFFFFFFF }, -- Stockholm Lidingöbanan 21
  ["1275002500001"] = { "25", 0xFF03AAAE, 0xFFFFFFFF }, -- Stockholm Saltsjöbanan 25
  ["1275002600001"] = { "26", 0xFF03AAAE, 0xFFFFFFFF }, -- Stockholm Saltsjöbanan 26
  ["1275002700001"] = { nil, 0xFFA05EA5, 0xFFFFFFFF }, -- Roslagsbanan 27
  ["1275002700002"] = { nil, 0xFFA05EA5, 0xFFFFFFFF }, -- Roslagsbanan 27
  ["1275002800001"] = { nil, 0xFFA05EA5, 0xFFFFFFFF }, -- Roslagsbanan 28
  ["1275002800002"] = { nil, 0xFFA05EA5, 0xFFFFFFFF }, -- Roslagsbanan 28
  ["1275002800003"] = { nil, 0xFFA05EA5, 0xFFFFFFFF }, -- Roslagsbanan 28
  ["1275002900001"] = { nil, 0xFFA05EA5, 0xFFFFFFFF }, -- Roslagsbanan 29
  ["1275003000001"] = { "30", 0xFFFF9900, 0xFFFFFFFF }, -- Stockholm Tvärbanan 30
  ["1275003100001"] = { "31", 0xFFFF9900, 0xFFFFFFFF }, -- Stockholm Tvärbanan 31
  ["1275000000001"] = { nil, 0xFFF266A6, 0xFFFFFFFF }, -- Stockholm pendeltåg
  ["1275000000002"] = { nil, 0xFFF266A6, 0xFFFFFFFF }, -- Stockholm pendeltåg
  ["1275000000003"] = { nil, 0xFFF266A6, 0xFFFFFFFF }, -- Stockholm pendeltåg
  ["1275000000004"] = { nil, 0xFFF266A6, 0xFFFFFFFF }, -- Stockholm pendeltåg
  ["1279500100001"] = { "1", 0xFFFFFFFF, 0xFF01ABE9 }, -- Göteborg tram 1
  ["1279500200001"] = { "2", 0xFFFEDC00, 0xFF01ABE9 }, -- Göteborg tram 2
  ["1279500300001"] = { "3", 0xFF006EB9, 0xFFFFFFFF }, -- Göteborg tram 3
  ["1279500400001"] = { "4", 0xFF029254, 0xFFFFFFFF }, -- Göteborg tram 4
  ["1279500500001"] = { "5", 0xFFE82835, 0xFFFFFFFF }, -- Göteborg tram 5
  ["1279500600001"] = { "6", 0xFFF49311, 0xFF03ABE7 }, -- Göteborg tram 6
  ["1279500700001"] = { "7", 0xFF9D5701, 0xFFFFFFFF }, -- Göteborg tram 7
  ["1279500800001"] = { "8", 0xFFA9378E, 0xFFFFFFFF }, -- Göteborg tram 8
  ["1279500900001"] = { "9", 0xFF80CDF4, 0xFF22B4EC }, -- Göteborg tram 9
  ["1279501000001"] = { "10", 0xFFD0DE87, 0xFF00ABE9 }, -- Göteborg tram 10
  ["1279501100001"] = { "11", 0xFF1B1A18, 0xFFFFFFFF }, -- Göteborg tram 11
  ["1279501200001"] = { "12", 0xFF57B9A8, 0xFF04303B }, -- Göteborg tram 12
  ["1251000100001"] = { "1", 0xFFFDFEFF, 0xFF49606C }, -- UL bus 1
  ["1251000200001"] = { "2", 0xFFB01216, 0xFFFDFEFF }, -- UL bus 2
  ["1251000300001"] = { "3", 0xFF00A551, 0xFFFDFEFF }, -- UL bus 3
  ["1251000400001"] = { "4", 0xFFED5BA1, 0xFFFDFEFF }, -- UL bus 4
  ["1251000500001"] = { "5", 0xFF88B848, 0xFFFDFEFF }, -- UL bus 5
  ["1251000600001"] = { "6", 0xFF8E7355, 0xFFFDFEFF }, -- UL bus 6
  ["1251000700001"] = { "7", 0xFF00BCF2, 0xFFFDFEFF }, -- UL bus 7
  ["1251000800001"] = { "8", 0xFFF27022, 0xFFFDFEFF }, -- UL bus 8
  ["1251000900001"] = { "9", 0xFF0089D0, 0xFFFDFEFF }, -- UL bus 9
  ["1251001000001"] = { "10", 0xFF97268F, 0xFFFDFEFF }, -- UL bus 10
  ["1251001100001"] = { "11", 0xFF929598, 0xFFFDFEFF }, -- UL bus 11
  ["1251001200001"] = { "12", 0xFFFCB915, 0xFF49606C }, -- UL bus 12
  ["1251001300001"] = { "13", 0xFFDDC3DE, 0xFF49606C }, -- UL bus 13
  ["1251001400001"] = { "14", 0xFF69CBD9, 0xFF49606C }, -- UL bus 14
  ["1251002100001"] = { "21", 0xFFF27022, 0xFFFDFEFF }, -- UL bus 21
  ["1251002200001"] = { "22", 0xFF0089D0, 0xFFFDFEFF }, -- UL bus 22
  ["1251002300001"] = { "23", 0xFF00A551, 0xFFFDFEFF }, -- UL bus 23
  ["1251003100001"] = { "31", 0xFFFCB915, 0xFF49606C }, -- UL bus 31
  ["1251003200001"] = { "32", 0xFF0089D0, 0xFFFDFEFF }, -- UL bus 32
  ["1251003300001"] = { "33", 0xFF00A551, 0xFFFDFEFF }, -- UL bus 33
  ["1251003400001"] = { "34", 0xFFB01216, 0xFFFDFEFF } -- UL bus 34
}

-- override route_type based on route_id
local route_id_route_type_map = {
  ["1276076300001"] = 800 -- trolley bus (line 3) in Landskrona
}

function process_route(route)
  local route_type_map = agency_route_type_map[route:get_agency():get_name()]
  local route_id_map = route_id_short_name_color_map[route:get_id()]
  local route_type = route_id_route_type_map[route:get_id()]

  if route_type_map then
    local m = route_type_map[route:get_route_type()]

    if m then
      route:set_clasz(m[1])
      route:set_route_type(m[2])
    end
  end

  if route_id_map then
    local short_name = route_id_map[1]
    local color = route_id_map[2]
    local text_color = route_id_map[3]

    if short_name then
      route:set_short_name(short_name)
    end
    if color then
      route:set_color(color)
    end
    if text_color then
      route:set_text_color(text_color)
    end
  end

  if route_type then
    route:set_route_type(route_type)
  end
end
