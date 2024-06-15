{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchResults where

import Data.DateTime (DateTime)
import Data.Either (hush)
import Data.Functor (map)
import Data.Maybe (Maybe)
import Effect.Aff (Aff)
import Effect.Class (liftEffect)
import Effect.Now (nowDateTime)
import Elmish (Dispatch, ReactElement, Transition, forkMaybe)
import Elmish.HTML.Styled as H
import Motis (Position, Connection, parseData, sendIntermodalRoutingRequest)
import Prelude (pure, bind, discard, (#), ($))
import Web.HTML (window)
import Web.HTML.Location (search)
import Web.HTML.Window (location)
import Web.URL.URLSearchParams as SearchParams

type PositionQuery = { position :: Position }

data Message
  = Query Position Position DateTime
  | ReceivedConnections (Array Connection)

type State =
  { connections :: Array Connection
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
  now <- liftEffect nowDateTime
  pure do
    from <- SearchParams.get "fromLocation" params
    to <- SearchParams.get "toLocation" params
    fromPos <- hush (parseData from) :: Maybe PositionQuery
    toPos <- hush (parseData to) :: Maybe PositionQuery
    pure (Query fromPos.position toPos.position now)

init :: Transition Message State
init = do
  forkMaybe startSearch

  pure
    { connections: []
    }

update :: State -> Message -> Transition Message State
update state (ReceivedConnections connections) = pure state { connections = connections }
update state (Query from to departure) = do
  forkMaybe do
    resp <- sendIntermodalRoutingRequest from to departure
    pure $ map (\r -> ReceivedConnections r.connections) resp

  pure state

view :: State -> Dispatch Message -> ReactElement
view state _dispatch = H.ul "" $ map connectionEntry state.connections
  where
  connectionEntry connection = H.ul "card" $ map transportEntry connection.transports
  transportEntry transport = H.li "" transport.move_type
