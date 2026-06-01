function process_trip(trip)
    trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
end