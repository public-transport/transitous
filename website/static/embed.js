function createTransitousWidget(parent, start, destination) {
	let f = start ? window.TransitousWidget.location(start) : window.TransitousWidget.noLocation
	let t = destination ? window.TransitousWidget.location(destination) : window.TransitousWidget.noLocation
	window.TransitousWidget.main(parent)(f)(t)()
}
