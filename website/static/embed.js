/*
SPDX-FileCopyrightText: 2025 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
*/

function createTransitousWidget(parent, start, destination) {
	let f = start ? window.TransitousWidget.location(start) : window.TransitousWidget.noLocation
	let t = destination ? window.TransitousWidget.location(destination) : window.TransitousWidget.noLocation
	window.TransitousWidget.main(parent)(f)(t)()
}
