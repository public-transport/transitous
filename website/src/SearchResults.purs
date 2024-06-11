{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchResults where

import Prelude (pure, ($), (<<<), bind, discard, (#))

import Elmish (Transition, Dispatch, ReactElement)
import Elmish.HTML.Styled as H
import Elmish.Component (fork)

import Web.HTML (window)
import Web.HTML.Window (location)
import Web.HTML.Location (search)
import Web.URL.URLSearchParams as SearchParams

import Data.Unit (Unit)
import Data.Maybe (Maybe(..))

import Effect.Class (liftEffect)
import Effect.Aff (Aff)


type Connnection = Unit

data Message = Query SearchParams.URLSearchParams
             | ReceivedConnections (Array Connnection)

type State =
  {
  }

getSearchParams :: Aff SearchParams.URLSearchParams
getSearchParams = do
  liftEffect do
    w <- window
    loc <- w # location
    url <- loc # search
    pure (SearchParams.fromString url)

startSearch :: Aff Message
startSearch = do
    params <- getSearchParams
    let from = SearchParams.get "fromLocation" params
    let to = SearchParams.get "toLocation" params
    pure (Query params)

init :: Transition Message State
init = do
  fork startSearch

  pure {}

update :: State -> Message -> Transition Message State
update state (ReceivedConnections connections) = pure state
update state (Query l) = pure state

view :: State -> Dispatch Message -> ReactElement
view state dispatch = H.span "" "Hello world"
