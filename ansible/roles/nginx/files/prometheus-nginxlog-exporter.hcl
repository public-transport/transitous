# SPDX-FileCopyrightText: 2025 Traines <git@traines.eu>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

listen {
  port    = 4040
  address = "10.11.0.1"
}

namespace "rp" {
  format = "[$time_local] $host rl=$request_length urt=$upstream_response_time rt=$request_time bbs=$body_bytes_sent s=$status ph=$proxy_host uri=$uri ua=$http_user_agent"

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
    from         = "proxy_host"
  }

  relabel "uri" {
    from         = "uri"
    match "^/api/(v[0-9]{1,2})/(geocode|reverse-geocode|stoptimes|map/stops|map/initial|map/trips|map/levels|rentals|trip|plan|one-to-all|one-to-many|debug).*" {
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
}