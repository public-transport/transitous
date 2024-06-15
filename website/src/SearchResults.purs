{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchResults where

import Data.Argonaut.Encode (toJsonString)
import Data.Either (hush)
import Data.Maybe (Maybe(..))
import Data.Unit (Unit)
import Effect.Aff (Aff)
import Effect.Class (liftEffect)
import Elmish (Dispatch, ReactElement, Transition, forkMaybe)
import Elmish.HTML.Styled as H
import Motis (Position, logAff, parseData, sendIntermodalRoutingRequest)
import Prelude (pure, bind, discard, (#), show)
import Web.HTML (window)
import Web.HTML.Location (search)
import Web.HTML.Window (location)
import Web.URL.URLSearchParams as SearchParams


type Connnection = Unit

type PositionQuery = { position :: Position }

data Message = Query PositionQuery PositionQuery
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

startSearch :: Aff (Maybe Message)
startSearch = do
    params <- getSearchParams
    pure do
      from <- SearchParams.get "fromLocation" params
      to <- SearchParams.get "toLocation" params
      fromPos <- hush (parseData from)
      toPos <- hush (parseData to)
      pure (Query fromPos toPos)

init :: Transition Message State
init = do
  forkMaybe startSearch

  pure {}

update :: State -> Message -> Transition Message State
update state (ReceivedConnections connections) = pure state
update state (Query from to) = do
  forkMaybe do
    resp <- sendIntermodalRoutingRequest from.position to.position
    logAff (show (toJsonString resp))
    pure Nothing

  pure {}

view :: State -> Dispatch Message -> ReactElement
view state dispatch = H.span "" "Hello world"
