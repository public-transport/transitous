{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchResults where

import Prelude

import Data.Array (head, last, modifyAt, (!!))
import Data.DateTime (DateTime, Time, hour, minute, time)
import Data.DateTime.Instant (instant, toDateTime)
import Data.Enum (fromEnum)
import Data.String as String
import Data.Functor (mapFlipped)
import Data.Int (toNumber)
import Data.Maybe (Maybe(..), fromMaybe)
import Data.Time.Duration (Seconds(..), convertDuration)
import Data.Tuple (Tuple(..))
import Effect.Class (liftEffect)
import Elmish (Dispatch, ReactElement, Transition, forkMaybe, (<|))
import Elmish.HTML.Styled as H
import Motis (Connection, RouteQuery, getQueryFromUrl, sendIntermodalRoutingRequest)
import Utils (enumerate, filterMaybe)

data Message
  = Query RouteQuery
  | ReceivedConnections (Array Connection)
  | ToggleConnection Int

type State =
  { connections :: Array Connection
  , expandedConnections :: Array Boolean
  , loading :: Boolean
  }

init :: Transition Message State
init = do
  forkMaybe do
    query <- liftEffect getQueryFromUrl
    pure $ map Query query

  pure
    { connections: []
    , expandedConnections: []
    , loading: false
    }

update :: State -> Message -> Transition Message State
update state (ReceivedConnections connections) =
  pure state
    { connections = connections
    , expandedConnections = map (\_ -> false) connections
    , loading = false
    }
update state (Query { from, to, departure }) = do
  forkMaybe do
    resp <- sendIntermodalRoutingRequest from to departure
    pure $ map (\r -> ReceivedConnections r.connections) resp

  pure state { loading = true }
update state (ToggleConnection i) = do
  case modifyAt i not state.expandedConnections of
    Just newConns -> pure state { expandedConnections = newConns }
    Nothing -> pure state

moveTypeIcon :: String -> String
moveTypeIcon = case _ of
  "Transport" -> "bi-train-front-fill"
  "Walk" -> "bi-person-walking"
  _ -> "bi-patch-question-fill"

moveTypeText :: String -> String
moveTypeText = case _ of
  "Transport" -> "Take public transport"
  "Walk" -> "Walk"
  _ -> ""

classIcon :: Int -> String
classIcon = case _ of
  10 -> "bi-bus-front-fill"
  7 -> "bi-train-front-fill"
  1 -> "bi-train-front-fill"
  _ -> "bi-train-front-fill"

unixToDateTime :: Int -> Maybe DateTime
unixToDateTime seconds = do
  inst <- instant (convertDuration (Seconds (toNumber seconds)))
  Just (toDateTime inst)

formatTime :: Time -> String
formatTime time = pad (show (fromEnum (hour time)))
  <> ":"
  <> pad (show (fromEnum (minute time)))
  where
  pad str = if String.length str < 2 then "0" <> str else str

formatUnixTime :: Int -> String
formatUnixTime unix =
  unix
    # unixToDateTime
    # map time
    # map formatTime
    # fromMaybe ""

formatStartTime :: Connection -> String
formatStartTime connection =
  head connection.stops
    # map (_.departure.time)
    # map formatUnixTime
    # fromMaybe ""

formatArrivalTime :: Connection -> String
formatArrivalTime connection =
  last connection.stops
    # map (_.arrival.time)
    # map formatUnixTime
    # fromMaybe ""

displayConnectionDetails :: Connection -> Int -> Dispatch Message -> ReactElement
displayConnectionDetails connection i dispatch =
  H.button_ "card mb-4 p-4 flex-col text-start w-100" { onClick: dispatch <| ToggleConnection i } $
    [ H.text (formatStartTime connection) ]
      <> mapFlipped connection.transports
        ( \transport -> do
            let
              to =
                connection.stops !! transport.move.range.to
                  # filterMaybe (\s -> s.station.name /= "END")
                  # map (_.station.name)

              icon =
                map classIcon transport.move.clasz
                  # fromMaybe (moveTypeIcon transport.move_type)

              time =
                connection.stops !! transport.move.range.to
                  # filterMaybe (\s -> s.station.name /= "END")
                  # map (_.departure.time)
                  # map formatUnixTime

              lineName = fromMaybe "" transport.move.name

            H.span ""
              ( [ H.div "m-3"
                    [ H.span "rounded transport-icon p-1"
                        [ H.i_ ("m-2 bi " <> icon) { title: moveTypeText transport.move_type } ""
                        , H.text lineName
                        ]
                    ]
                ] <> case to of
                  Just dest -> case time of
                    Just t -> [ H.span "me-4" t, H.span "fw-bold" dest ]
                    Nothing -> []
                  Nothing -> []
              )
        )
      <> [ H.text (formatArrivalTime connection) ]

displayConnection :: Connection -> Int -> Dispatch Message -> ReactElement
displayConnection connection i dispatch =
  H.button_ "card mb-4 p-4 flex-row" { onClick: dispatch <| ToggleConnection i } $
    [ H.span "me-2" (formatStartTime connection) ]
      <> mapFlipped connection.transports
        ( \transport -> do
            let
              icon = fromMaybe (moveTypeIcon transport.move_type) (map classIcon transport.move.clasz)

            H.div "" $
              [ H.span "m-1"
                  [ H.span "rounded transport-icon p-1"
                      [ H.i_ ("m-2 bi " <> icon) { title: moveTypeText transport.move_type } ""
                      , H.text (fromMaybe "" transport.move.name)
                      ]
                  ]
              ]
        )
      <>
        [ H.span "ms-2" (formatArrivalTime connection) ]

view :: State -> Dispatch Message -> ReactElement
view state dispatch = case state.loading of
  true -> H.div "d-flex justify-content-center" $
    [ H.div_ "spinner-border mt-5" { role: "status" }
        [ H.span "visually-hidden" ""
        ]
    ]
  false -> H.div "" $
    mapFlipped (enumerate state.connections) \(Tuple i connection) -> do
      case fromMaybe false (state.expandedConnections !! i) of
        true -> displayConnectionDetails connection i dispatch
        false -> displayConnection connection i dispatch
