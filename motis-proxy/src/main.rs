// SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

#[macro_use]
extern crate rocket;

mod rate_limit;

use log::{trace, warn};
use reqwest::{Client, StatusCode};
use rocket::{
    http::Status,
    http::{self, ContentType},
    response::status::Custom,
    serde::json::Json,
    State,
};
use rocket_cors::{AllowedOrigins, CorsOptions};
use serde::{Deserialize, Serialize};
use serde_default::DefaultFromSerde;
use serde_repr::*;

use std::{net::IpAddr, num::NonZeroUsize, time::Duration};

use rate_limit::IpRateLimit;

// For documetation generation
use rocket_okapi::okapi::schemars;
use rocket_okapi::okapi::schemars::JsonSchema;
use rocket_okapi::settings::UrlObject;
use rocket_okapi::{openapi, openapi_get_routes, rapidoc::*};

pub type ResultResponse<T> = Result<T, Custom<()>>;

fn default_connections_per_host() -> usize {
    100
}
fn default_timeout() -> u64 {
    10
}
fn default_motis_address() -> String {
    "http://localhost:8080".to_string()
}
fn default_proxy_assets() -> bool {
    false
}
fn default_allowed_endpoints() -> Option<Vec<Endpoint>> {
    None
}
fn default_routes_per_minute_limit() -> u16 {
    20
}
fn default_lru_rate_limit_entries() -> usize {
    10_000
}

#[derive(Deserialize, DefaultFromSerde)]
struct Config {
    #[serde(default = "default_connections_per_host")]
    connections_per_host: usize,
    #[serde(default = "default_timeout")]
    timeout: u64,
    #[serde(default = "default_motis_address")]
    motis_address: String,

    /// Proxy endpoints other than `/`. This should only ever be used for debugging.
    /// It is slow and incomplete.
    #[serde(default = "default_proxy_assets")]
    proxy_assets: bool,

    /// List of endpoints (by path) that should be allowed through the proxy.
    /// If this option is not set, all known endpoints will be allowed.
    #[serde(default = "default_allowed_endpoints")]
    allowed_endpoints: Option<Vec<Endpoint>>,

    #[serde(default = "default_routes_per_minute_limit")]
    routes_per_minute_limit: u16,

    #[serde(default = "default_lru_rate_limit_entries")]
    lru_rate_limit_entries: usize,
}

#[derive(Deserialize, Serialize, PartialEq, Eq, JsonSchema)]
enum Endpoint {
    /// Endpoint for routing. This endpoint tries to find a route using the optimal mix of modes of transportation.
    #[serde(rename = "/intermodal")]
    Intermodal,
    /// Endpoint for for completing station names
    #[serde(rename = "/guesser")]
    Guesser,
    #[serde(rename = "/address")]
    Address,
    #[serde(rename = "/railviz/get_trains")]
    RailVizGetTrains,
    #[serde(rename = "/railviz/get_trips")]
    RailVizGetTrips,
    #[serde(rename = "/lookup/schedule_info")]
    LookupScheduleInfo,
    #[serde(rename = "/gbfs/info")]
    GbfsInfo,
    #[serde(rename = "/railviz/get_station")]
    RailVizGetStation,
    #[serde(rename = "/ppr/route")]
    PprRoute,
    #[serde(rename = "/trip_to_connection")]
    TripId,
}

#[derive(Deserialize, Serialize, JsonSchema)]
#[serde(tag = "type")]
enum RequestDestination {
    Module { target: Endpoint },
}

#[derive(Deserialize, Serialize, JsonSchema)]
enum StartType {
    /// The user is planning in advance and has not boarded any vehicles yet.
    /// The optimal mode of transportation from their coordinates should be chosen automatically.
    IntermodalPretripStart,
    /// Similar to `IntermodalPretripStart`, but starting from a station.
    /// See [Pretrip Start](https://motis-project.de/docs/api/endpoint/intermodal.html#pretrip-start) in the MOTIS documentation.
    PretripStart,
    /// See [Intermodal Ontrip Start](https://motis-project.de/docs/api/endpoint/intermodal.html#intermodal-ontrip-start) in the MOTIS documentation.
    IntermodalOntripStart,
    /// The user is already at a station or the trip is supposed to start from a station. The planned departure time is already known.
    /// See [Ontrip Station Start](https://motis-project.de/docs/api/endpoint/intermodal.html#ontrip-station-start) in the MOTIS documentation.
    OntripStationStart,
    /// The user is already on a train and wants to find connections from there.
    /// See [Ontrip Train Start](https://motis-project.de/docs/api/endpoint/intermodal.html#ontrip-train-start) in the MOTIS documentation.
    OntripTrainStart,
}

#[derive(Deserialize, Serialize, JsonSchema)]
enum DestinationType {
    /// The `destination` is a `Station`
    InputStation,
    /// The `destination` is a `GeoLocation`
    InputPosition,
}

/// See [Interval](https://motis-project.de/docs/api/buildingblocks.html#interval) in the MOTIS documentation for more details.
#[derive(Deserialize, Serialize, JsonSchema)]
struct Interval {
    /// Unix time stamp
    begin: u64,
    /// Unix time stamp
    end: u64,
}

/// See [Position](https://motis-project.de/docs/api/buildingblocks.html#position) in the MOTIS Documentation for more details.
#[derive(Deserialize, Serialize, JsonSchema)]
struct GeoLocation {
    /// Latitude
    lat: f32,
    /// Longitude
    lng: f32,
}

/// See [Station](https://motis-project.de/docs/api/buildingblocks.html#station)
/// in the MOTIS documentation for more details.
#[derive(Deserialize, Serialize, JsonSchema)]
struct Station {
    /// Station identifier. Can be retrieved using a `StationGuesserRequest` or `LookupGeoStationRequest`.
    id: String,
    /// Station name
    name: String,
    /// Station position
    pos: GeoLocation,
}

/// See [Input Station](https://motis-project.de/docs/api/buildingblocks.html#input-station)
/// in the MOTIS documentation for more details.
#[derive(Deserialize, Serialize, JsonSchema)]
struct InputStation {
    /// Station identifier. Can be retrieved using a `StationGuesserRequest` or `LookupGeoStationRequest`.
    id: String,
    /// Station name
    name: String,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct Start {
    #[serde(skip_serializing_if = "Option::is_none")]
    position: Option<GeoLocation>,
    #[serde(skip_serializing_if = "Option::is_none")]
    station: Option<InputStation>,
    /// Time interval in which the connection should be. If there is none in the interval, connections close to the requested interval will be returned.
    interval: Interval,
    /// The minimum number of connections to be found until stopping to increase the time interval. Please note that the actual number of returned connections may be less, if finding more connections takes a very long time. This can happen if a connection is only available very few times.
    min_connection_count: u8,
    /// Whether to include earlier connections if not enough are found in the requested time interval.
    extend_interval_earlier: bool,
    /// Whether to include later connections if not enough are found in the requested time interval.
    extend_interval_later: bool,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct FootSearchOptions {
    /// PPR profile, for example `"default"`
    profile: String,
    /// Duration limit in seconds
    duration_limit: u32,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct PprOptions {
    search_options: FootSearchOptions,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct BikeOptions {
    /// Duration limit in seconds
    max_duration: u32,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct CarOptions {
    /// Duration limit in seconds
    max_duration: u32,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct CarParkingOptions {
    /// Duration limit in seconds
    max_car_duration: u32,
    ppr_search_options: FootSearchOptions,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct GBFSOptions {
    provider: String,
    max_walk_duration: u32,
    max_vehicle_duration: u32,
}

/// See [Modes](https://motis-project.de/docs/api/endpoint/intermodal.html#modes) in the MOTIS documentation.
#[derive(Deserialize, Serialize, JsonSchema)]
#[serde(tag = "mode_type", content = "mode")]
enum TransportMode {
    /// Walking
    FootPPR(PprOptions),
    /// Riding a bicycle
    Bike(BikeOptions),
    /// Driving a car
    Car(CarOptions),
    /// Driving a car including finding a location to park near the station
    CarParking(CarParkingOptions),
    GBFS(GBFSOptions),
}

#[derive(Deserialize, Serialize, JsonSchema)]
#[serde(untagged)]
enum Location {
    Geo(GeoLocation),
    Station(InputStation),
}

#[derive(Deserialize, Serialize, JsonSchema)]
enum SearchType {
    r#Default,
    Accessibility,
}

#[derive(Deserialize, Serialize, JsonSchema)]
enum SearchDirection {
    /// Search from start to destination
    Forward,
    /// Search from destination to start, useful when searching by arrival time.
    Backward,
}

#[derive(Deserialize, Serialize, JsonSchema)]
enum AllowedRouters {
    /// The default routing engine
    #[serde(rename = "")]
    DefaultRouter,
}

#[derive(Serialize_repr, Deserialize_repr, JsonSchema)]
#[repr(u8)]
enum AllowedClasses {
    Air = 0,
    HighSpeed = 1,
    LongDistance = 2,
    Coach = 3,
    Night = 4,
    RegionalFast = 5,
    Regional = 6,
    Metro = 7,
    Subway = 8,
    Tram = 9,
    Bus = 10,
    Ship = 11,
    Other = 12
}

/// See [Intermodal Routing](https://motis-project.de/docs/api/endpoint/intermodal.html#intermodal-routing-request) in the MOTIS documentation for more details.
#[derive(Deserialize, Serialize, JsonSchema)]
struct IntermodalConnectionRequest {
    /// Situation for which a connection should be searched
    start_type: StartType,
    /// The start location
    start: Start,
    /// Transport modes to consider for the start of the trip
    start_modes: Vec<TransportMode>,
    /// Type of destination
    destination_type: DestinationType,
    /// The destination location
    destination: Location,
    /// Modes of transport to consider for the arrival
    destination_modes: Vec<TransportMode>,
    search_type: SearchType,
    search_dir: SearchDirection,
    router: AllowedRouters,
    #[serde(skip_serializing_if = "Option::is_none")]
    allowed_claszes: Option<Vec<AllowedClasses>>
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct StationGuesserRequest {
    /// Maximum number of guesses to return
    guess_count: u8,
    /// User input to guess from
    input: String,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct AddressRequest {
    input: String,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct RailVizTrainsRequest {
    zoom_bounds: u8,
    zoom_geo: u8,
    corner1: Location,
    corner2: Location,
    max_trains: u16,
    last_trains: u16,
    /// Unix time stamp
    start_time: u64,
    /// Unix time stamp
    end_time: u64,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct Trip {
    id: String,
    line_id: String,
    station_id: String,
    target_station_id: String,
    /// Unix time stamp
    target_time: u64,
    /// Unix time stamp
    time: u64,
    train_nr: u32,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct RailVizTripsRequest {
    trips: Vec<Trip>,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct MotisNoMessage {}

#[derive(Deserialize, Serialize, JsonSchema)]
enum StationDepartureDirection {
    #[serde(rename = "BOTH")]
    Both,
    #[serde(rename = "EARLIER")]
    Earlier,
    #[serde(rename = "LATER")]
    Later,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct RailVizStationRequest {
    station_id: String,
    /// Unix time stamp
    time: u64,
    event_count: u16,
    direction: StationDepartureDirection,
    by_schedule_time: bool,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct FootRoutingRequest {
    destinations: Vec<Location>,
    include_edges: bool,
    include_path: bool,
    include_steps: bool,
    search_options: FootSearchOptions,
    start: Location,
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct TripId {
    id: String,
    station_id: String,
    train_nr: u32,
    /// Unix time stamp
    time: u64,
    target_station_id: String,
    /// Unix time stamp
    target_time: u64,
    line_id: String,
}

#[derive(Deserialize, Serialize, JsonSchema)]
#[serde(tag = "content_type", content = "content")]
enum RequestContent {
    /// This request can be sent to the `/intermodal` target
    IntermodalConnectionRequest(IntermodalConnectionRequest),
    /// This request can be sent to the `/intermodal` target
    IntermodalRoutingRequest(IntermodalConnectionRequest),
    /// This request can be sent to the `/guesser` target
    StationGuesserRequest(StationGuesserRequest),
    /// This request can be sent to the `/address` target
    AddressRequest(AddressRequest),
    /// This request can be sent to the `/railviz/get_trains` target
    RailVizTrainsRequest(RailVizTrainsRequest),
    /// This request can be sent to the `/railviz/get_trips` target
    RailVizTripsRequest(RailVizTripsRequest),
    /// This request can be sent to the `/lookup/schedule_info` or the `/gbfs/info` target
    MotisNoMessage(MotisNoMessage),
    /// This request can be sent to the `/railviz/get_station` target
    RailVizStationRequest(RailVizStationRequest),
    /// This request can be sent to the `/ppr/route` target
    FootRoutingRequest(FootRoutingRequest),
    /// This request can be sent to the `/trip_to_connection` target
    TripId(TripId),
}

#[derive(Deserialize, Serialize, JsonSchema)]
struct Request {
    destination: RequestDestination,
    #[serde(flatten)]
    content: RequestContent,
}

/// # MOTIS API
///
/// All MOTIS requests need to be sent to this URL. For Transitous, it is located at `https://routing.spline.de/api/`.
///
/// You can use the destination field to choose the endpoint to call.
///
/// Have a look at what the MOTIS web interface sends for examples.
///
#[openapi(tag = "MOTIS")]
#[post("/", format = "application/json", data = "<request>", rank = 2)]
async fn proxy_api(
    request: Json<Request>,
    http_client: &State<Client>,
    config: &State<Config>,
    route_rate_limit: &State<IpRateLimit>,
    remote_address: IpAddr,
) -> ResultResponse<Custom<Json<serde_json::Value>>> {
    let request = request.into_inner();

    // Check if the requested endpoint is allowed
    match &request.destination {
        RequestDestination::Module { target } => {
            if let Some(allowed_endpoints) = &config.allowed_endpoints {
                if !allowed_endpoints.contains(target) {
                    return Err(Custom(Status::UnprocessableEntity, ()));
                }
            }
        }
    }

    // Check if routing limit was exceeded
    if matches!(
        request.content,
        RequestContent::IntermodalConnectionRequest(_)
            | RequestContent::IntermodalRoutingRequest(_)
    ) && route_rate_limit.should_limit(&remote_address)
    {
        return Err(Custom(Status::TooManyRequests, ()));
    }

    trace!("MOTIS Request <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<");
    if let Ok(json) = serde_json::to_string_pretty(&request) {
        trace!("{json}");
    }

    let response = http_client
        .post(&config.motis_address)
        .json(&request)
        .send()
        .await
        .map_err(|error| {
            if error.is_timeout() {
                return Custom(Status::GatewayTimeout, ());
            }

            if error.is_connect() {
                return Custom(Status::BadGateway, ());
            }

            let error_code = error
                .status()
                .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR)
                .as_u16();

            Custom(Status::new(error_code), ())
        })?;

    let status = response.status().as_u16();

    let json = response
        .json::<serde_json::Value>()
        .await
        .map_err(|_| Custom(Status::InternalServerError, ()))?;

    trace!("MOTIS Response >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>");
    if let Ok(json) = serde_json::to_string_pretty(&json) {
        trace!("{json}");
    }

    Ok(Custom(Status::new(status), Json(json)))
}

///
/// This is only used for development, in a real deployment this should be done by a real web server.
/// This implementation is very inefficient and buffers everything in RAM.
///
#[get("/<_..>")]
async fn proxy_everything<'r>(
    uri: &http::uri::Origin<'r>,
    http_client: &State<Client>,
    config: &State<Config>,
) -> ResultResponse<Custom<(ContentType, Vec<u8>)>> {
    let upstream_url = format!("{}{}", config.motis_address, uri);

    trace!("Proxing to upstream url: {upstream_url}");

    let response = http_client
        .get(&upstream_url)
        .send()
        .await
        .map_err(|error| {
            let error_code = error
                .status()
                .unwrap_or(StatusCode::INTERNAL_SERVER_ERROR)
                .as_u16();

            Custom(Status::new(error_code), ())
        })?;

    let status = response.status().as_u16();
    let headers = response.headers();
    let content_type = headers
        .get("content-type")
        .and_then(|content_type| content_type.to_str().ok())
        .and_then(ContentType::parse_flexible)
        .unwrap_or(ContentType::Any);

    let body = response
        .bytes()
        .await
        .map_err(|_| Custom(Status::InternalServerError, ()))?;

    Ok(Custom(Status::new(status), (content_type, body.to_vec())))
}

#[launch]
fn rocket() -> _ {
    let cors = CorsOptions {
        allowed_origins: AllowedOrigins::All,
        send_wildcard: true,
        ..Default::default()
    }
    .to_cors()
    .expect("Invalid cors options");

    let rocket = rocket::build();

    let config: Config = match rocket.figment().extract_inner("proxy") {
        Ok(config) => config,
        Err(e) => {
            warn!("Falling back to default config because: {e}");
            Config::default()
        }
    };

    let mut routes = openapi_get_routes![proxy_api];
    if config.proxy_assets {
        routes.append(&mut routes![proxy_everything]);
    }

    rocket
        .manage(
            Client::builder()
                .timeout(Duration::from_secs(config.timeout))
                .pool_max_idle_per_host(config.connections_per_host)
                .build()
                .expect("Invalid options"),
        )
        .attach(cors.clone())
        .manage(cors)
        .manage(IpRateLimit::new(
            NonZeroUsize::new(config.lru_rate_limit_entries)
                .expect("lru_rate_limit_entries must not be zero"),
            config.routes_per_minute_limit,
        ))
        .manage(config)
        .mount("/", routes)
        .mount("/", rocket_cors::catch_all_options_routes())
        .mount(
            "/doc/",
            make_rapidoc(&RapiDocConfig {
                title: Some("Transitous API".to_string()),
                general: GeneralConfig {
                    spec_urls: vec![UrlObject::new("General", "../openapi.json")],
                    heading_text: "Transitous API".to_string(),
                    ..Default::default()
                },
                hide_show: HideShowConfig {
                    allow_spec_url_load: false,
                    allow_spec_file_load: false,
                    allow_try: false,
                    allow_authentication: false,
                    allow_server_selection: false,
                    show_info: false,
                    ..Default::default()
                },
                ui: UiConfig {
                    // Don't use Google Fonts
                    load_fonts: false,
                    header_color: "#F4AB45".to_string(),
                    primary_color: "#F4AB45".to_string(),
                    bg_color: "#FFFFFF".to_string(),
                    font_size: FontSize::Large,
                    ..Default::default()
                },
                nav: NavConfig {
                    nav_bg_color: "#F5F5F5".to_string(),
                    ..Default::default()
                },
                schema: SchemaConfig {
                    schema_expand_level: 3,
                    schema_description_expanded: true,
                    ..Default::default()
                },
                ..Default::default()
            }),
        )
}
