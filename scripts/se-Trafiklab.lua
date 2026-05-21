-- SPDX-FileCopyrightText: Marcus Lundblad <ml@dfupdate.se>
-- SPDX-License-Identifier: AGPL-3.0-or-later

-- map input route type to MOTIS clasz/output route type
local agency_route_type_map = {
  ["DVVJ"] = {
    [102] = { 107 } -- map DVVJ from long distance rail to tourist rail
  },
  ["Lennakatten"] = {
    [102] = { 107 } -- map Lennakatten from long distance rail to tourist rail
  },
  ["TJF Smalspåret"] = {
    [102] = { 107 } -- map TJF from long distance rail to tourist rail
  }
}

-- override route colors based on agency name and short_name
local route_agency_short_name_color_map = {
  ["Kiruna Stadstrafik"] = {
    ["Grön"] = { 0xFF83A72A, 0xFFFFFFFF },
    ["Gul."] = { 0xFFF9B000, 0xFF000000 },
    ["Lila."] = { 0xFF8D4895, 0xFFFFFFFF },
    ["RÖD"] = { 0xFFE30513, 0xFFFFFFFF },
    ["Röd."] = { 0xFFE30513, 0xFFFFFFFF }
  },
  ["SL"] = {
    ["7"] = { 0xFF999999, 0xFFFFFFFF }, -- Stockholm tram 7
    ["10"] = { 0xFF0089CA, 0xFFFFFFFF }, -- Stockholm metro 10 (blue line)
    ["11"] = { 0xFF0089CA, 0xFFFFFFFF }, -- Stockholm metro 11 (blue line)
    ["13"] = { 0xFFD71D24, 0xFFFFFFFF }, -- Stockholm metro 13 (red line)
    ["14"] = { 0xFFD71D24, 0xFFFFFFFF }, -- Stockholm metro 14 (red line)
    ["17"] = { 0xFF04A64A, 0xFFFFFFFF }, -- Stockholm metro 17 (green line)
    ["18"] = { 0xFF04A64A, 0xFFFFFFFF }, -- Stockholm metro 18 (green line)
    ["19"] = { 0xFF04A64A, 0xFFFFFFFF }, -- Stockholm metro 19 (green line)
    ["25"] = { 0xFF03AAAE, 0xFFFFFFFF }, -- Stockholm Saltsjöbanan 25
    ["26"] = { 0xFF03AAAE, 0xFFFFFFFF } -- Stockholm Saltsjöbanan 26
  },
  ["UL"] = {
    ["1"] = { 0xFFFDFEFF, 0xFF49606C }, -- UL bus 1
    ["2"] = { 0xFFB01216, 0xFFFDFEFF }, -- UL bus 2
    ["3"] = { 0xFF00A551, 0xFFFDFEFF }, -- UL bus 3
    ["4"] = { 0xFFED5BA1, 0xFFFDFEFF }, -- UL bus 4
    ["5"] = { 0xFF88B848, 0xFFFDFEFF }, -- UL bus 5
    ["6"] = { 0xFF8E7355, 0xFFFDFEFF }, -- UL bus 6
    ["7"] = { 0xFF00BCF2, 0xFFFDFEFF }, -- UL bus 7
    ["8"] = { 0xFFF27022, 0xFFFDFEFF }, -- UL bus 8
    ["9"] = { 0xFF0089D0, 0xFFFDFEFF }, -- UL bus 9
    ["10"] = { 0xFF97268F, 0xFFFDFEFF }, -- UL bus 10
    ["11"] = { 0xFF929598, 0xFFFDFEFF }, -- UL bus 11
    ["12"] = { 0xFFFCB915, 0xFF49606C }, -- UL bus 12
    ["13"] = { 0xFFDDC3DE, 0xFF49606C }, -- UL bus 13
    ["14"] = { 0xFF69CBD9, 0xFF49606C }, -- UL bus 14
    ["21"] = { 0xFFF27022, 0xFFFDFEFF }, -- UL bus 21
    ["22"] = { 0xFF0089D0, 0xFFFDFEFF }, -- UL bus 22
    ["23"] = { 0xFF00A551, 0xFFFDFEFF }, -- UL bus 23
    ["31"] = { 0xFFFCB915, 0xFF49606C }, -- UL bus 31
    ["32"] = { 0xFF0089D0, 0xFFFDFEFF }, -- UL bus 32
    ["33"] = { 0xFF00A551, 0xFFFDFEFF }, -- UL bus 33
    ["34"] = { 0xFFB01216, 0xFFFDFEFF } -- UL bus 34
  },
  ["VL"] = {
    ["1"] = { 0xFFDF494C, 0xFFFDFEFF }, -- Västerås bus 1
    ["2"] = { 0xFF00A96A, 0xFFFDFEFF }, -- Västerås bus 2
    ["3"] = { 0xFFF39DC3, 0xFFFDFEFF }, -- Västerås bus 3
    ["4"] = { 0xFF12ADE4, 0xFFFDFEFF }, -- Västerås bus 4
    ["5"] = { 0xFFFDCB35, 0xFFFDFEFF }, -- Västerås bus 5
    ["6"] = { 0xFFF4832D, 0xFFFDFEFF }, -- Västerås bus 6
    ["7"] = { 0xFFA777B4, 0xFFFDFEFF }, -- Västerås bus 7
    ["14"] = { 0xFFA7A39F, 0xFFFFFFFF }, -- Västerås bus 14
    ["15"] = { 0xFFA7A39F, 0xFFFFFFFF } -- Västerås bus 15
  },
  ["Värmlandstrafik"] = {
    ["S"] = { 0xFFBF1A35, 0xFFFDFEFF },
    ["1"] = { 0xFFFAAF19, 0xFF000114 },
    ["2"] = { 0xFF0BB14C, 0xFFFDFEFF },
    ["4"] = { 0xFF00AABD, 0xFFFDFEFF },
    ["5"] = { 0xFFF48221, 0xFFFDFEFF },
    ["6"] = { 0xFF003C69, 0xFFFDFEFF },
    ["7"] = { 0xFFD6118C, 0xFFFDFEFF },
    ["8"] = { 0xFF0072BC, 0xFFFDFEFF },
    ["10"] = { 0xFF8B2B91, 0xFFFDFEFF },
    ["11"] = { 0xFF8B2B91, 0xFFFDFEFF },
    ["12"] = { 0xFF8B2B91, 0xFFFDFEFF },
    ["13"] = { 0xFF8B2B91, 0xFFFDFEFF },
    ["22"] = { 0xFF000114, 0xFFFDFEFF },
    ["50"] = { 0xFF5C6263, 0xFFFDFEFF },
    ["51"] = { 0xFFFCB915, 0xFFFDFEFF },
    ["52"] = { 0xFF6EBF45, 0xFFFDFEFF },
    ["56"] = { 0xFF004182, 0xFFFDFEFF },
    ["57"] = { 0xFFD6118C, 0xFFFDFEFF },
    ["58"] = { 0xFF5AC7F3, 0xFFFDFEFF },
    ["59"] = { 0xFF00743E, 0xFFFDFEFF },
    ["84"] = { 0xFF00AABD, 0xFFFDFEFF },
    ["85"] = { 0xFFF48221, 0xFFFDFEFF },
    ["86"] = { 0xFF004182, 0xFFFDFEFF },
    ["87"] = { 0xFFD6118C, 0xFFFDFEFF },
    ["98"] = { 0xFF5AC7F3, 0xFFFDFEFF }
  },
  ["X-trafik"] = {
    -- Lines 1-4 have local variants in Gävleborg in Gävle, Söderhamn, Hudiksvall
    -- sharing the same colors
    ["1"] = { 0xFF139046, 0xFFFDFEFF },
    ["2"] = { 0xFFEC1F25, 0xFFFDFDFE },
    ["3"] = { 0xFF005DA1, 0xFFFDFEFF },
    ["4"] = { 0xFFFECB09, 0xFF221F21 },
    ["11"] = { 0xFFA5A9AC, 0xFF221F21 },
    ["12"] = { 0xFFA5A9AC, 0xFF221F21 },
    ["14"] = { 0xFFA5A9AC, 0xFF221F21 },
    ["15"] = { 0xFFA5A9AC, 0xFF221F21 }
  }
}

-- override route colors based on agency name and long_name
local route_agency_long_name_color_map = {
  ["SL"] = {
    ["Nockebybanan"] = { 0xFF669999, 0xFFFFFFFF }, -- Stockholm Nockebybanan 12
    ["Lidingöbanan"] = { 0xFFB66931, 0xFFFFFFFF }, -- Stockholm Lidingöbanan 21
    ["Roslagsbanan"] = { 0xFFA05EA5, 0xFFFFFFFF }, -- Roslagsbanan 27, 28, 29
    ["Tvärbanan"] = { 0xFFFF9900, 0xFFFFFFFF }, -- Stockholm Tvärbanan 30, 31
    ["Pendeltåg"] = { 0xFFF266A6, 0xFFFFFFFF } -- Stockholm pendeltåg
  }
}

-- override route colors based on agency name, route type, and short_name
local route_agency_type_short_name_color_map = {
  ["Västtrafik"] = {
    [900] = {
       ["1"] = { 0xFFFFFFFF, 0xFF01ABE9 }, -- Göteborg tram 1
       ["2"] = { 0xFFFEDC00, 0xFF01ABE9 }, -- Göteborg tram 2
       ["3"] = { 0xFF006EB9, 0xFFFFFFFF }, -- Göteborg tram 3
       ["4"] = { 0xFF029254, 0xFFFFFFFF }, -- Göteborg tram 4
       ["5"] = { 0xFFE82835, 0xFFFFFFFF }, -- Göteborg tram 5
       ["6"] = { 0xFFF49311, 0xFF03ABE7 }, -- Göteborg tram 6
       ["7"] = { 0xFF9D5701, 0xFFFFFFFF }, -- Göteborg tram 7
       ["8"] = { 0xFFA9378E, 0xFFFFFFFF }, -- Göteborg tram 8
       ["9"] = { 0xFF80CDF4, 0xFF22B4EC }, -- Göteborg tram 9
       ["10"] = { 0xFFD0DE87, 0xFF00ABE9 }, -- Göteborg tram 10
       ["11"] = { 0xFF1B1A18, 0xFFFFFFFF }, -- Göteborg tram 11
       ["12"] = { 0xFF57B9A8, 0xFF04303B }, -- Göteborg tram 12
       ["13"] = { 0xFFFDCC99, 0xFF00435C }, -- Göteborg tram 13
       ["14"] = { 0xFFD7B1F4, 0xFF7D43FF }, -- Göteborg tram 14
       ["X"] = { 0xFFFFFFFF, 0xFFFF0000 } -- Göteborg tram X
    }
  },
  ["Östgötatrafiken"] = {
     [900] = {
       ["2"] = { 0xFFCD0000, 0xFFFFFFFF }, -- Norrköping tram 2
       ["3"] = { 0xFF008000, 0xFFFFFFFF } -- Norrköping tram 3
     }
  }
}

-- override route_short_name and route colors based on route_id
local route_id_short_name_color_map = {
  ["1265000300001"] = { "3", 0xFFD98A7E, 0xFF000114 }, -- Karlstad bus 3
  ["1265106300001"] = { "3", 0xFFBF282E, 0xFFFDFEFF }, -- Kristinehamn bus 3
  ["1279501600001"] = { "16", 0xFF007C4F, 0xFFFFFF50 }, -- Göteborg stombuss 16
  ["1279501700001"] = { "17", 0xFF00008E, 0xFFFFFF50 }, -- Göteborg stombuss 17
  ["1279501800001"] = { "18", 0xFF323232, 0xFFFFFF50 }, -- Göteborg stombuss 18
  ["1279501900001"] = { "19", 0xFFE0005B, 0xFFFFFF50 } -- Göteborg stombuss 19
}

-- override route_type based on route_id
local route_id_route_type_map = {
  ["1276076300001"] = 800 -- trolley bus (line 3) in Landskrona
}

function set_colors(route, map)
  local color = map[1]
  local text_color = map[2]

  if color then
    route:set_color(color)
  end
  if text_color then
    route:set_text_color(text_color)
  end
end

function process_route(route)
  local route_type_map = agency_route_type_map[route:get_agency():get_name()]
  local route_id_map = route_id_short_name_color_map[route:get_id()]
  local agency_route_short_name_map =
    route_agency_short_name_color_map[route:get_agency():get_name()]
  local agency_type_route_short_name_map =
    route_agency_type_short_name_color_map[route:get_agency():get_name()]
  local agency_route_long_name_map =
    route_agency_long_name_color_map[route:get_agency():get_name()]
  local route_type = route_id_route_type_map[route:get_id()]

  if route_type_map then
    local m = route_type_map[route:get_route_type()]

    if m then
      route:set_route_type(m[1])
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

  if agency_route_short_name_map then
    local map = agency_route_short_name_map[route:get_short_name()]

    if map then
      set_colors(route, map)
    end
  end

  if agency_type_route_short_name_map then
    local map = agency_type_route_short_name_map[route:get_route_type()]

    if map then
      local map_name = map[route:get_short_name()];

      if map_name then
        set_colors(route, map_name)
      end
    end
  end

  if agency_route_long_name_map then
    local map = agency_route_long_name_map[route:get_long_name()]

    if map then
      set_colors(route, map)
    end
  end

  if route_type then
    route:set_route_type(route_type)
  end
end
