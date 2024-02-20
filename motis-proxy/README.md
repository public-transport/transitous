# MOTIS Proxy

This proxy validates all incoming requests before forwarding them to MOTIS.
It ensures that the request is:

* valid JSON
* a valid motis request
* to an endpoint we actually want to expose

It should only be used to handle the `/` endpoint of motis, everything else should be proxied using a proper web server.

## Development

For development, you can set up a `Rocket.toml` with the following content in the working directory of `motis-proxy`.

With the debug log level, it will log the requests and responses.

```toml
[default.proxy]
motis_address = "https://europe.motis-project.de"

[default]
log_level = "debug"
```

<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: none
-->
