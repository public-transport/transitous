{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module MotisForward where

import Prelude (($), show)

import Data.FormURLEncoded (fromArray, encode)
import Data.Maybe (Maybe(..), fromMaybe)
import Data.Tuple (Tuple(..))
import Data.Semigroup ((<>))

import SearchBox

formatCoordinates :: Location -> String
formatCoordinates { lat, lon } = show lat <> "," <> show lon

getIdentifier :: Location -> String
getIdentifier loc = case loc.type of
  "ADDRESS" -> formatCoordinates loc
  "PLACE" -> formatCoordinates loc
  "STOP" -> loc.id
  _ -> formatCoordinates loc

toMotisWebUrl :: Location -> Location -> String
toMotisWebUrl start destination = motisInstance <> "?" <> urlQuery
  where
  urlQuery = fromMaybe "" $ encode $ fromArray
    [ Tuple "fromPlace" (Just (getIdentifier start))
    , Tuple "toPlace" (Just (getIdentifier destination))
    , Tuple "fromName" (Just start.name)
    , Tuple "toName" (Just destination.name)
    ]
