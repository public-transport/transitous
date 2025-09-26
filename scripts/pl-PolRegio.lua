function process_trip(trip)
	if trip:get_route():get_short_name() == "REG" then
		trip:set_display_name("R " .. trip:get_short_name())
	else
		trip:set_display_name(trip:get_route():get_short_name() .. " " .. trip:get_short_name())
	end
end

function process_route(route)
	if route:get_short_name() == "REG" then
		route:set_clasz(6)
	elseif route:get_short_name() == "IR" then
		route:set_clasz(5)
	elseif route:get_short_name() == "ZKA REG" then
		route:set_clasz(10)
		route:set_route_type(714) -- rail replacement bus
	end
end
