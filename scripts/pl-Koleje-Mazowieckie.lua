function process_route(route)
    if route:get_id() == "ZL" then
        route:set_clasz(10)
        route:set_route_type(700)
	elseif string.find(route:get_id(), "Z") then
		route:set_clasz(10)
		route:set_route_type(714) --rail replacement bus
	elseif string.find(route:get_id(), "RE") then
		route:set_clasz(5)
	else
		route:set_clasz(6)
	end
	return true
end
