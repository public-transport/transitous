{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module MotisForward where

import SearchBox

import Data.DateTime (DateTime)
import Data.Either (hush)
import Data.FormURLEncoded (fromArray, encode)
import Data.Formatter.DateTime (formatDateTime)
import Data.Maybe (Maybe(..), fromMaybe)
import Data.Semigroup ((<>))
import Data.Tuple (Tuple(..))
import Prelude (($), show)

formatCoordinates :: Location -> String
formatCoordinates { lat, lon } = show lat <> "," <> show lon

getIdentifier :: Location -> String
getIdentifier loc = case loc.type of
  "ADDRESS" -> formatCoordinates loc
  "PLACE" -> formatCoordinates loc
  "STOP" -> loc.id
  _ -> formatCoordinates loc

toMotisWebUrl :: Location -> Location -> DateTime -> Boolean -> String
toMotisWebUrl start destination dateTime arriveBy = motisInstance <> "?" <> urlQuery
  where
  urlQuery = fromMaybe "" $ encode $ fromArray
    [ Tuple "fromPlace" (Just (getIdentifier start))
    , Tuple "toPlace" (Just (getIdentifier destination))
    , Tuple "fromName" (Just start.name)
    , Tuple "toName" (Just destination.name)
    , Tuple "time" (hush $ formatDateTime "YYYY-MM-DDTHH:mm" dateTime)
    , Tuple "arriveBy" (Just $ show $ arriveBy)
    ]
