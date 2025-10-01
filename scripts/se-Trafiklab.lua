-- SPDX-FileCopyrightText: Marcus Lundblad <ml@dfupdate.se>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- map input route type to MOTIS clasz/output route type
local agency_route_type_map = {
  ["DVVJ"] = {
    [102] = { 2, 107 } -- map DVVJ from long distance rail to tourist rail
  },
  ["Lennakatten"] = {
    [102] = { 2, 107 } -- map Lennakatten from long distance rail to tourist rail
  },
  ["TJF Smalspåret"] = {
    [102] = { 2, 107 } -- map TJF from long distance rail to tourist rail
  }
}

-- override route_short_name and route colors based on route_id
local route_id_short_name_color_map = {
  [1275000700001] = { "7", "999999", "FFFFFF" }, -- Stockholm tram 7
  [1275001000001] = { "10", "0089CA", "FFFFFF" }, -- Stockholm metro 10 (blue line)
  [1275001100001] = { "11", "0089CA", "FFFFFF" }, -- Stockholm metro 11 (blue line)
  [1275001200001] = { "12", "669999", "FFFFFF" }, -- Stockholm Nockebybanan 12
  [1275001300001] = { "13", "D71D24", "FFFFFF" }, -- Stockholm metro 13 (red line)
  [1275001400001] = { "14", "D71D24", "FFFFFF" }, -- Stockholm metro 14 (red line)
  [1275001700001] = { "17", "04A64A", "FFFFFF" }, -- Stockholm metro 17 (green line)
  [1275001800001] = { "18", "04A64A", "FFFFFF" }, -- Stockholm metro 18 (green line)
  [1275001900001] = { "19", "04A64A", "FFFFFF" }, -- Stockholm metro 19 (green line)
  [1275002100001] = { "21", "B66931", "FFFFFF" }, -- Stockholm Lidingöbanan 21
  [1275002500001] = { "25", "03AAAE", "FFFFFF" }, -- Stockholm Saltsjöbanan 25
  [1275002600001] = { "26", "03AAAE", "FFFFFF" }, -- Stockholm Saltsjöbanan 26
  [1275002700001] = { "27", "A05EA5", "FFFFFF" }, -- Roslagsbanan 27
  [1275002700002] = { "27", "A05EA5", "FFFFFF" }, -- Roslagsbanan 27
  [1275002800001] = { "28", "A05EA5", "FFFFFF" }, -- Roslagsbanan 28
  [1275002800002] = { "28", "A05EA5", "FFFFFF" }, -- Roslagsbanan 28
  [1275002800003] = { "28", "A05EA5", "FFFFFF" }, -- Roslagsbanan 28
  [1275002900001] = { "29", "A05EA5", "FFFFFF" }, -- Roslagsbanan 29
  [1275003000001] = { "30", "FF9900", "FFFFFF" }, -- Stockholm Tvärbanan 30
  [1275003100001] = { "31", "FF9900", "FFFFFF" }, -- Stockholm Tvärbanan 31
  [1275000000001] = { nil, "F266A6", "FFFFFF" }, -- Stockholm pendeltåg
  [1275000000002] = { nil, "F266A6", "FFFFFF" }, -- Stockholm pendeltåg
  [1275000000003] = { nil, "F266A6", "FFFFFF" }, -- Stockholm pendeltåg
  [1275000000004] = { nil, "F266A6", "FFFFFF" }, -- Stockholm pendeltåg
  [1279500100001] = { "1", "FFFFFF", "01ABE9" }, -- Göteborg tram 1
  [1279500200001] = { "2", "FEDC00", "01ABE9" }, -- Göteborg tram 2
  [1279500300001] = { "3", "006EB9", "FFFFFF" }, -- Göteborg tram 3
  [1279500400001] = { "4", "029254", "FFFFFF" }, -- Göteborg tram 4
  [1279500500001] = { "5", "E82835", "FFFFFF" }, -- Göteborg tram 5
  [1279500600001] = { "6", "F49311", "03ABE7" }, -- Göteborg tram 6
  [1279500700001] = { "7", "9D5701", "FFFFFF" }, -- Göteborg tram 7
  [1279500800001] = { "8", "A9378E", "FFFFFF" }, -- Göteborg tram 8
  [1279500900001] = { "9", "80CDF4", "22B4EC" }, -- Göteborg tram 9
  [1279501000001] = { "10", "D0DE87", "00ABE9" }, -- Göteborg tram 10
  [1279501100001] = { "11", "1B1A18", "FFFFFF" }, -- Göteborg tram 11
  [1279501200001] = { "12", "B3B3B3", "306CB7" }, -- Göteborg tram 12
  [1251000100001] = { "1", "FDFEFF", "49606C" }, -- UL bus 1
  [1251000200001] = { "2", "B01216", "FDFEFF" }, -- UL bus 2
  [1251000300001] = { "3", "00A551", "FDFEFF" }, -- UL bus 3
  [1251000400001] = { "4", "ED5BA1", "FDFEFF" }, -- UL bus 4
  [1251000500001] = { "5", "88B848", "FDFEFF" }, -- UL bus 5
  [1251000600001] = { "6", "8E7355", "FDFEFF" }, -- UL bus 6
  [1251000700001] = { "7", "00BCF2", "FDFEFF" }, -- UL bus 7
  [1251000800001] = { "8", "F27022", "FDFEFF" }, -- UL bus 8
  [1251000900001] = { "9", "0089D0", "FDFEFF" }, -- UL bus 9
  [1251001000001] = { "10", "97268F", "FDFEFF" }, -- UL bus 10
  [1251001100001] = { "11", "929598", "FDFEFF" }, -- UL bus 11
  [1251001200001] = { "12", "FCB915", "49606C" }, -- UL bus 12
  [1251001300001] = { "13", "DDC3DE", "49606C" }, -- UL bus 13
  [1251001400001] = { "14", "69CBD9", "49606C" }, -- UL bus 14
  [1251002100001] = { "21", "F27022", "FDFEFF" }, -- UL bus 21
  [1251002200001] = { "22", "0089D0", "FDFEFF" }, -- UL bus 22
  [1251002300001] = { "23", "00A551", "FDFEFF" }, -- UL bus 23
  [1251003100001] = { "31", "FCB915", "49606C" }, -- UL bus 31
  [1251003200001] = { "32", "0089D0", "FDFEFF" }, -- UL bus 32
  [1251003300001] = { "33", "00A551", "FDFEFF" }, -- UL bus 33
  [1251003400001] = { "34", "B01216", "FDFEFF" } -- UL bus 34
}

-- override route_type based on route_id
local route_id_route_type_map = {
  [1276076300001] = 800 -- trolley bus (line 3) in Landskrona
}

function process_route(route)
  local route_type_map = agency_route_type_map[route:get_agency():get_name()]
  local route_id_map = route_id_short_name_color_map[route:get_route_id()]
  local route_type = route_id_route_type_map[route:get_route_id()]

  if route_type_map then
    local m = route_type_map[route:get_route_type()]

    if m then
      route:set_clasz(m[1])
      route:set_route_type(m[2])
    end
  end

  if route_id_map then
    local short_name = route_id_map[1]
    local route_color = route_id_map[2]
    local route_text_color = route_id_map[3]

    if short_name then
      route:set_route_short_name(short_name)
    end
    if route_color then
      route:set_route_color(route_color)
    end
    if route_text_color then
      route:set_route_text_color(route_text_color)
    end
  end

  if route_type then
    route:set_route_type(route_type)
  end
end
