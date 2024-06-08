{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module Motis (sendAddressRequest, sendStationRequest, Address(..), Station(..), Position(..), Region(..)) where

import Prelude

import Data.Either (Either(..))
import Data.Maybe (Maybe(..))
import Effect.Class (liftEffect)
import Effect.Console (log)
import Effect.Aff (Aff)

import Data.Argonaut.Decode (decodeJson, class DecodeJson)
import Data.Argonaut.Decode.Parser (parseJson)
import Data.Argonaut.Decode.Error (JsonDecodeError)
import Data.Argonaut.Encode (toJsonString, class EncodeJson)

import Fetch (Method(..), fetch)


-- Requests
type StationGuesserRequest = { input :: String, guess_count :: Int }
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

-- Response
type Position = { lat :: Number, lng :: Number }
type Station = { id :: String, name :: String, pos :: Position }
type StationResponse = { content :: { guesses :: Array Station } }

type Region = { name :: String, admin_level :: Int }
type Address = { pos :: Position, name :: String, type :: String, regions :: Array Region }
type AddressResponse = { content :: { guesses :: Array Address } }


parseMotisResponse :: forall a. DecodeJson a => String -> Either JsonDecodeError a
parseMotisResponse text = do
  decoded <- parseJson text
  decodeJson decoded

logAff :: String -> Aff Unit
logAff = log >>> liftEffect

sendMotisRequest :: forall a. DecodeJson a => String -> Aff (Maybe a)
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
    let result = parseMotisResponse responseBody
    case result of
      Left err -> do
        logAff (show err)
        pure Nothing
      Right response -> pure (Just response)

sendStationRequest :: String -> Aff (Maybe StationResponse)
sendStationRequest = stationRequest >>> sendMotisRequest

sendAddressRequest :: String -> Aff (Maybe AddressResponse)
sendAddressRequest = addressRequest >>> sendMotisRequest
