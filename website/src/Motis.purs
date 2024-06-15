{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module Motis where

import Prelude

import Data.Argonaut.Decode (decodeJson, class DecodeJson)
import Data.Argonaut.Decode.Class (class DecodeJsonField)
import Data.Argonaut.Decode.Error (JsonDecodeError)
import Data.Argonaut.Decode.Parser (parseJson)
import Data.Argonaut.Encode (toJsonString, class EncodeJson)
import Data.DateTime (DateTime)
import Data.DateTime.Instant (fromDateTime, unInstant)
import Data.Either (Either(..))
import Data.Int (floor)
import Data.Maybe (Maybe(..))
import Data.Time.Duration (Seconds(..), convertDuration)
import Effect.Aff (Aff)
import Effect.Class (liftEffect)
import Effect.Console (log)
import Fetch (Method(..), fetch)

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
stationRequest text = serializeMotisRequest
  { content_type: "StationGuesserRequest"
  , destination:
      { type: "Module"
      , target: "/guesser"
      }
  , content:
      { input: text
      , guess_count: 6
      }
  }

addressRequest :: String -> String
addressRequest text = serializeMotisRequest
  { content_type: "AddressRequest"
  , destination:
      { type: "Module"
      , target: "/address"
      }
  , content:
      { input: text }
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
dateTimeToUnix dateTime = let (Seconds unixTime) = convertDuration (unInstant (fromDateTime dateTime)) in floor unixTime

-- Responses
type MotisResponse a = { content :: a }

type StationResponse = { guesses :: Array Station }

type AddressResponse = { guesses :: Array Address }

type Connection =
  { transports ::
      Array
        { move_type :: String
        , move ::
            { direction :: Maybe String
            , line_id :: Maybe String
            , name :: Maybe String
            , provider :: Maybe String
            }
        }
  }

type IntermodalRoutingResponse = { connections :: Array Connection }

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
