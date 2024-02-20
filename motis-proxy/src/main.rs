// SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

#[macro_use]
extern crate rocket;

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
use log::{trace, warn};

use std::time::Duration;

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
    #[serde(default = "default_proxy_assets" )]
    proxy_assets: bool
}

#[derive(Deserialize, Serialize)]
enum AllowedEndpoints {
    #[serde(rename = "/intermodal")]
    Intermodal,
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
}

#[derive(Deserialize, Serialize)]
#[serde(tag = "type")]
enum RequestDestination {
    Module { target: AllowedEndpoints },
}

#[derive(Deserialize, Serialize)]
enum StartDestinationType {
    IntermodalPretripStart,
    PretripStart,
    IntermodalOntripStart,
    InputStation,
    InputPosition,
}

#[derive(Deserialize, Serialize)]
struct Interval {
    begin: u64,
    end: u64,
}

#[derive(Deserialize, Serialize)]
struct GeoLocation {
    lat: f32,
    lng: f32,
}

#[derive(Deserialize, Serialize)]
struct StationLocation {
    id: String,
    name: String,
}

#[derive(Deserialize, Serialize)]
struct Start {
    #[serde(skip_serializing_if = "Option::is_none")]
    position: Option<GeoLocation>,
    #[serde(skip_serializing_if = "Option::is_none")]
    station: Option<StationLocation>,
    interval: Interval,
    min_connection_count: u8,
    extend_interval_earlier: bool,
    extend_interval_later: bool,
}

#[derive(Deserialize, Serialize)]
struct FootSearchOptions {
    profile: String,
    duration_limit: u32,
}

#[derive(Deserialize, Serialize)]
struct PprOptions {
    search_options: FootSearchOptions,
}

#[derive(Deserialize, Serialize)]
struct BikeOptions {
    max_duration: u32,
}

#[derive(Deserialize, Serialize)]
struct CarOptions {
    max_duration: u32,
}

#[derive(Deserialize, Serialize)]
struct CarParkingOptions {
    max_car_duration: u32,
    ppr_search_options: PprOptions,
}

#[derive(Deserialize, Serialize)]
#[serde(tag = "mode_type", content = "mode")]
enum TransportMode {
    FootPPR(PprOptions),
    Bike(BikeOptions),
    Car(CarOptions),
    CarParking(CarParkingOptions),
}

#[derive(Deserialize, Serialize)]
#[serde(untagged)]
enum Location {
    Geo(GeoLocation),
    Station(StationLocation),
}

#[derive(Deserialize, Serialize)]
enum SearchType {
    r#Default,
    Accessibility,
}

#[derive(Deserialize, Serialize)]
enum SearchDirection {
    Forward,
    Backward,
}

#[derive(Deserialize, Serialize)]
enum AllowedRouters {
    #[serde(rename = "")]
    DefaultRouter,
}

#[derive(Deserialize, Serialize)]
struct IntermodalConnectionRequest {
    start_type: StartDestinationType,
    start: Start,
    start_modes: Vec<TransportMode>,
    destination_type: StartDestinationType,
    destination: Location,
    destination_modes: Vec<TransportMode>,
    search_type: SearchType,
    search_dir: SearchDirection,
    router: AllowedRouters,
}

#[derive(Deserialize, Serialize)]
struct StationGuesserRequest {
    guess_count: u8,
    input: String,
}

#[derive(Deserialize, Serialize)]
struct AddressRequest {
    input: String,
}

#[derive(Deserialize, Serialize)]
struct RailVizTrainsRequest {
    zoom_bounds: u8,
    zoom_geo: u8,
    corner1: Location,
    corner2: Location,
    max_trains: u16,
    last_trains: u16,
    start_time: u64,
    end_time: u64,
}

#[derive(Deserialize, Serialize)]
struct Trip {
    id: String,
    line_id: String,
    station_id: String,
    target_station_id: String,
    target_time: u64,
    time: u64,
    train_nr: u32,
}

#[derive(Deserialize, Serialize)]
struct RailVizTripsRequest {
    trips: Vec<Trip>,
}

#[derive(Deserialize, Serialize)]
struct MotisNoMessage {}

#[derive(Deserialize, Serialize)]
enum StationDepartureDirection {
    #[serde(rename = "BOTH")]
    Both,
}

#[derive(Deserialize, Serialize)]
struct RailVizStationRequest {
    station_id: String,
    time: u64,
    event_count: u16,
    direction: StationDepartureDirection,
    by_schedule_time: bool,
}

#[derive(Deserialize, Serialize)]
struct FootRoutingRequest {
    destinations: Vec<Location>,
    include_edges: bool,
    include_path: bool,
    include_steps: bool,
    search_options: FootSearchOptions,
    start: Location,
}

#[derive(Deserialize, Serialize)]
#[serde(tag = "content_type", content = "content")]
enum RequestContent {
    IntermodalConnectionRequest(IntermodalConnectionRequest),
    IntermodalRoutingRequest(IntermodalConnectionRequest),
    StationGuesserRequest(StationGuesserRequest),
    AddressRequest(AddressRequest),
    RailVizTrainsRequest(RailVizTrainsRequest),
    RailVizTripsRequest(RailVizTripsRequest),
    MotisNoMessage(MotisNoMessage),
    RailVizStationRequest(RailVizStationRequest),
    FootRoutingRequest(FootRoutingRequest)
}

#[derive(Deserialize, Serialize)]
struct Request {
    destination: RequestDestination,
    #[serde(flatten)]
    content: RequestContent
}

#[post("/", format = "application/json", data = "<request>", rank = 2)]
async fn proxy_api(
    request: Json<Request>,
    http_client: &State<Client>,
    config: &State<Config>,
) -> ResultResponse<Custom<Json<serde_json::Value>>> {
    let request = request.into_inner();

    trace!("MOTIS Request <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<");
    trace!("{}", serde_json::to_string_pretty(&request).unwrap());

    let response = http_client
        .post(&config.motis_address)
        .json(&request)
        .send()
        .await
        .map_err(|error| {
            if error.is_timeout() {
                return Custom(Status::GatewayTimeout, ())
            }

            if error.is_connect() {
                return Custom(Status::BadGateway, ())
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

    trace!("MOTIS Response >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", );
    trace!("{}", serde_json::to_string_pretty(&json).unwrap());

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
    let content_type = if let Some(content_type) = headers.get("content-type") {
        ContentType::parse_flexible(content_type.to_str().unwrap_or("application/octet-stream"))
            .unwrap()
    } else {
        ContentType::Any
    };

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

    let mut routes = routes![proxy_api];
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
        .manage(config)
        .mount("/", routes)
        .mount("/", rocket_cors::catch_all_options_routes())
}
