# SPDX-FileCopyrightText: 2025 Traines <git@traines.eu>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

listen {
  port    = 4040
  address = "10.11.0.1"
}

namespace "rp" {
  format = "[$time_local] $host rl=$request_length urt=$upstream_response_time rt=$request_time bbs=$body_bytes_sent s=$status ph=$upstream_addr uri=\"$uri\" l=\"$http_accept_language\" ua=\"$http_user_agent\""

  source {
    files = ["/var/log/nginx/metrics.log"]
  }

  relabel "host" {
    from         = "host"
    whitelist = [
      "api.transitous.org",
      "staging.api.transitous.org"
    ]
  }

  relabel "upstream" {
    from         = "upstream_addr"
  }

  relabel "uri" {
    from         = "uri"
    match "/+api/(v[0-9]{1,2}|experimental)/(health|geocode|reverse-geocode|stoptimes|map/stops|map/initial|map/trips|map/routes|map/levels|refresh-itinerary|rentals|trip|plan|one-to-all|one-to-many|one-to-many-intermodal|debug).*" {
      replacement = "/api/$1/$2"
    }

    match "^/gtfs.*" {
      replacement = "/gtfs"
    }

    match "^/tiles.*" {
      replacement = "/tiles"
    }

     match "^/_app.*" {
      replacement = "/_app"
    }

    match "^/.*" {
      replacement = "other"
    }
  }

  relabel "user_agent" {
    from         = "http_user_agent"

    match "^([A-Za-z0-9]{2}).*" {
      replacement = "$1*"
    }

    match "^.*" {
      replacement = "other"
    }
  }

  relabel "accept_language" {
    from         = "http_accept_language"

    match "^([a-z]{2}).*" {
      replacement = "$1*"
    }

    match "^.*" {
      replacement = "other"
    }
  }
}