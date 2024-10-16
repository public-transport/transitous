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

import SearchBox

toMotisWebUrl :: Location -> Location -> String
toMotisWebUrl start destination = "https://routing.spline.de/" <> urlQuery
  where
  urlQuery = fromMaybe "" $ encode $ fromArray
    [ Tuple "from" (Just (toJsonString start))
    , Tuple "to" (Just (toJsonString destination))
    ]
