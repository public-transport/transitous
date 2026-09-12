---
#template: home.html
title: For Data Producers
social:
  cards_layout_options:
    title: Free and Open Public Transport Routing
---

<!--
SPDX-FileCopyrightText: None
SPDX-License-Identifier: CC0-1.0
-->

If you publish open data for example for use in Transitous the following recommendations ensure we can use your data.

## Supported Formats

For schedules:

- GTFS
- NeTEx (may require changes on our side if a new profile is used)

For real-time updates:

- GTFS-RT
- SIRI-ET (XML/JSON)

## Supported GTFS Features

The following GTFS features are supported in our routing engine (MOTIS) and used in the Transitous deployment.
We recommend that you include data for them in your GTFS file if possible.

- [Fares V2](https://gtfs.org/community/extensions/fares-v2/)
- Shapes
- Translations
- Bikes Allowed
- Wheelchair Accessibility
- Flex
- [Google Transit Ticketing Extension](https://developers.google.com/transit/gtfs/reference/google-transit-ticketing-extension)
- [Google Transit Extended Route Types](https://developers.google.com/transit/gtfs/reference/extended-route-types)

## Supported GTFS-RT features

- Trip updates
- Alerts
- Vehicle Position (currently for our own delay calculation only)

## Recommended Licenses

The data should ideally be clearly licensed, even if you don't intend to restrict usage of the data in any way.
We recommend that you use an established standard license, as listed [here](https://opendefinition.org/licenses/).

## Recommended Web Server Features

- **Support for `Last-Modified` / `If-Last-Modified` headers**. 
  If this feature is not supported, files will be downloaded even if they didn't change, which wastes bandwidth for you and Transitous.
- **Stable, permanent download URL.**
  If the url changes, old data may be used in Transitous or your agency will temporarily not be covered until you or a contributor updates the URL on our side.
- **Allow automated downloads.** CAPTCHAS make it impossible to retrieve up to date data from you, since we need to fetch hundreds of sources every day.

## IP-Addresses

We download sources with the user-agent header `transitous.org` from the
following IP-addresses:

- `90.187.116.41` (rt.triptix.de)
- `130.83.165.222` (transitous.motis-project.de)
- `130.133.110.30` / `2001:470:51c5:babe::30:1`
  (crunchy.spline.inf.fu-berlin.de)
- `130.133.110.91` / `2001:470:51c5:babe::91:1` (vm-motis.spline.inf.fu-berlin.de)
