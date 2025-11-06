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
  }

  relabel "upstream" {
    from         = "proxy_host"
  }

  relabel "uri" {
    from         = "uri"
  }

  relabel "user_agent" {
    from         = "http_user_agent"
  }
}