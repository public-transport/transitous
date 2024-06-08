{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module MotisForward where

import Prelude (($))

import Data.Argonaut.Encode (toJsonString)

import Data.FormURLEncoded (fromArray, encode)
import Data.Maybe (Maybe(..), fromMaybe)
import Data.Tuple (Tuple(..))
import Data.Semigroup ((<>))

import SearchBox (Guess(..))
import Motis (Position, Station)

type StationMessage = { type :: String, station :: Station }

toStationMessage :: Station -> StationMessage
toStationMessage = { type: "Station", station: _ }

type PositionMessage = { type :: String, position :: Position }

toPositionMessage :: Position -> PositionMessage
toPositionMessage = { type: "Position", position: _ }

encodeEnd :: Guess -> String
encodeEnd = case _ of
  StationGuess station -> toJsonString $ toStationMessage station
  AddressGuess address -> toJsonString $ toPositionMessage address.pos

toMotisWebUrl :: Guess -> Guess -> String
toMotisWebUrl start destination = "https://routing.spline.de/?motis=https%3A%2F%2Frouting.spline.de%2Fapi&" <> urlQuery
  where
  urlQuery = fromMaybe "" $ encode $ fromArray
    [ Tuple "fromLocation" (Just (encodeEnd start))
    , Tuple "toLocation" (Just (encodeEnd destination))
    ]
