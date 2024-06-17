{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module Motis where

import Prelude

import Control.Alt (alt)
import Data.Argonaut.Decode (decodeJson, class DecodeJson)
import Data.Argonaut.Decode.Class (class DecodeJsonField)
import Data.Argonaut.Decode.Error (JsonDecodeError)
import Data.Argonaut.Decode.Parser (parseJson)
import Data.Argonaut.Encode (toJsonString, class EncodeJson)
import Data.DateTime (DateTime)
import Data.DateTime.Instant (fromDateTime, unInstant)
import Data.Either (Either(..), hush)
import Data.Int (floor)
import Data.Maybe (Maybe(..))
import Data.Time.Duration (Seconds(..), convertDuration)
import Effect (Effect)
import Effect.Aff (Aff)
import Effect.Class (liftEffect)
import Effect.Console (log)
import Effect.Now (nowDateTime)
import Fetch (Method(..), fetch)
import Web.HTML (window)
import Web.HTML.Location (search)
import Web.HTML.Window (location)
import Web.URL.URLSearchParams as SearchParams

-- Types
type Region = { name :: String, admin_level :: Int }
type Address = { pos :: Position, name :: String, type :: String, regions :: Array Region }

type Position = { lat :: Number, lng :: Number }
type Station = { id :: String, name :: String, pos :: Position }

-- Requests
type MotisRequest a = { content_type :: String, content :: a, destination :: { type :: String, target :: String } }

serializeMotisRequest :: forall a. (EncodeJson a) => MotisRequest a -> String
serializeMotisRequest = toJsonString

stationRequest :: String -> String
stationRequest query = serializeMotisRequest
  { content_type: "StationGuesserRequest"
  , destination:
      { type: "Module"
      , target: "/guesser"
      }
  , content:
      { input: query
      , guess_count: 6
      }
  }

addressRequest :: String -> String
addressRequest query = serializeMotisRequest
  { content_type: "AddressRequest"
  , destination:
      { type: "Module"
      , target: "/address"
      }
  , content:
      { input: query }
  }

intermodalRoutingRequest :: Position -> Position -> DateTime -> String
intermodalRoutingRequest start dest departure =
  serializeMotisRequest
    { content_type: "IntermodalRoutingRequest"
    , destination:
        { type: "Module"
        , target: "/intermodal"
        }
    , content:
        { start_type: "IntermodalPretripStart"
        , start_modes:
            [ { mode:
                  { search_options:
                      { duration_limit: 900
                      , profile: "default"
                      }
                  }
              , mode_type: "FootPPR"
              }
            ]
        , start:
            { extend_interval_earlier: false
            , extend_interval_later: true
            , interval:
                { begin: dateTimeToUnix departure
                , end: dateTimeToUnix departure
                }
            , min_connection_count: 5
            , position: start
            }
        , destination_modes:
            [ { mode:
                  { search_options:
                      { duration_limit: 900
                      , profile: "default"
                      }
                  }
              , mode_type: "FootPPR"
              }
            ]
        , destination_type: "InputPosition"
        , destination: dest
        , router: ""
        , search_dir: "Forward"
        , search_type: "Accessibility"
        }
    }

dateTimeToUnix :: DateTime -> Int
dateTimeToUnix dateTime =
  let
    (Seconds unixTime) = convertDuration (unInstant (fromDateTime dateTime))
  in
    floor unixTime

-- Responses
type MotisResponse a = { content :: a }

type StationResponse = { guesses :: Array Station }

type AddressResponse = { guesses :: Array Address }

type Stop = { station :: Station, departure :: { time :: Int }, arrival :: { time :: Int } }
type Transport =
  { move_type :: String
  , move ::
      { direction :: Maybe String
      , line_id :: Maybe String
      , name :: Maybe String
      , provider :: Maybe String
      , clasz :: Maybe Int
      , range ::
          { from :: Int
          , to :: Int
          }
      }
  }

type Trip = {}

type Connection =
  { stops :: Array Stop
  , transports :: Array Transport
  }

type IntermodalRoutingResponse = { connections :: Array Connection, interval_begin :: Int, interval_end :: Int }

-- Url query
type PositionQuery = { position :: Position }
type StationQuery = { station :: Station }

type RouteQuery =
  { from :: Position
  , to :: Position
  , departure :: DateTime
  }

getUrlSearchParams :: Effect SearchParams.URLSearchParams
getUrlSearchParams = do
  w <- window
  loc <- w # location
  queries <- loc # search
  pure (SearchParams.fromString queries)

getQueryFromUrl :: Effect (Maybe RouteQuery)
getQueryFromUrl = do
  params <- getUrlSearchParams
  now <- nowDateTime
  pure do
    fromJson <- SearchParams.get "fromLocation" params
    toJson <- SearchParams.get "toLocation" params

    -- Try to parse as either station or position, and take the one that worked
    let fromPosMsg = hush (parseData fromJson) :: Maybe PositionQuery
    let toPosMsg = hush (parseData toJson) :: Maybe PositionQuery
    let fromStationMsg = hush (parseData fromJson) :: Maybe StationQuery
    let toStationMsg = hush (parseData toJson) :: Maybe StationQuery

    from <- alt (map (_.position) fromPosMsg) (map (_.station.pos) fromStationMsg)
    to <- alt (map (_.position) toPosMsg) (map (_.station.pos) toStationMsg)

    Just { from, to, departure: now }

parseData :: forall a. DecodeJson a => String -> Either JsonDecodeError a
parseData text = do
  decoded <- parseJson text
  decodeJson decoded

logAff :: String -> Aff Unit
logAff = log >>> liftEffect

sendMotisRequest :: forall a. DecodeJsonField a => String -> Aff (Maybe a)
sendMotisRequest request = do
  let requestUrl = "https://routing.spline.de/api/"
  { status, statusText, text } <- fetch requestUrl
    { method: POST
    , headers: { "Content-Type": "application/json" }
    , body: request
    }
  responseBody <- text

  if status /= 200 then do
    logAff (statusText <> responseBody)
    pure Nothing
  else do
    let result = parseData responseBody
    case result of
      Left err -> do
        logAff (show err)
        pure Nothing
      Right response -> pure (Just (response :: MotisResponse a).content)

sendStationRequest :: String -> Aff (Maybe StationResponse)
sendStationRequest = stationRequest >>> sendMotisRequest

sendAddressRequest :: String -> Aff (Maybe AddressResponse)
sendAddressRequest = addressRequest >>> sendMotisRequest

sendIntermodalRoutingRequest :: Position -> Position -> DateTime -> Aff (Maybe IntermodalRoutingResponse)
sendIntermodalRoutingRequest start dest departure = intermodalRoutingRequest start dest departure
  # sendMotisRequest
