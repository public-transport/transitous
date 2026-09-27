-- Set this script on the CZPTT dataset in the MOTIS timetable configuration.
function process_trip(trip)
  local line = trip:get_route():get_short_name()
  local short_name = trip:get_short_name()

  if line ~= nil and line ~= "" and short_name ~= nil and short_name ~= "" then
    if line == short_name or line:sub(1, #short_name + 2) == short_name .. " (" then
      trip:set_display_name(line)
    else
      trip:set_display_name(line .. " (" .. short_name .. ")")
    end
  end
end
