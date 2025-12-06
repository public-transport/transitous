{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module TransitousWidget (main, location, noLocation) where

import Prelude

import Data.Bifunctor (bimap, lmap)
import Data.DateTime (DateTime, adjust)
import Data.Either (hush)
import Data.Formatter.DateTime (formatDateTime, unformatDateTime)
import Data.Maybe (Maybe(..), fromMaybe)
import Data.Time.Duration (negateDuration)
import Effect (Effect)
import Effect.Class (liftEffect)
import Effect.Now (getTimezoneOffset, nowDateTime)
import Elmish (Dispatch, ReactElement, Transition, forkMaybe, (<?|), (<|))
import Elmish.Boot (defaultMain)
import Elmish.HTML.Events as E
import Elmish.HTML.Styled as H
import MotisForward (toMotisWebUrl)
import SearchBox as SearchBox

data Message
  = DepartureMsg SearchBox.Message
  | ArrivalMsg SearchBox.Message
  | DateTimeChanged DateTime
  | ArriveByChanged Boolean

type State =
  { departureBox :: SearchBox.State
  , arrivalBox :: SearchBox.State
  , dateTime :: Maybe DateTime
  , arriveBy :: Boolean
  }

init :: Maybe SearchBox.Location -> Maybe SearchBox.Location -> Transition Message State
init from to = do
  departureState <- lmap DepartureMsg $ SearchBox.init "Start" from
  arrivalState <- lmap ArrivalMsg $ SearchBox.init "Destination" to
  forkMaybe do
    now <- liftEffect nowDateTime
    offset <- liftEffect getTimezoneOffset
    let dtime = adjust (negateDuration offset) now
    pure $ DateTimeChanged <$> dtime
  pure { departureBox: departureState, arrivalBox: arrivalState, dateTime: Nothing, arriveBy: false }

update :: State -> Message -> Transition Message State
update state (DepartureMsg msg) =
  bimap DepartureMsg state { departureBox = _ } $ SearchBox.update state.departureBox msg
update state (ArrivalMsg msg) =
  bimap ArrivalMsg state { arrivalBox = _ } $ SearchBox.update state.arrivalBox msg
update state (DateTimeChanged dt) = pure state { dateTime = Just dt }
update state (ArriveByChanged bool) = pure state { arriveBy = bool }

view :: State -> Dispatch Message -> ReactElement
view state dispatch = H.div "text-end card-body p-4"
  [ SearchBox.view state.departureBox (dispatch <<< DepartureMsg)
  , SearchBox.view state.arrivalBox (dispatch <<< ArrivalMsg)
  , H.input_ "form-control"
      { type: "datetime-local"
      , value: fromMaybe "" $ do
          dt <- state.dateTime
          hush (formatDateTime "YYYY-MM-DDTHH:mm" dt)
      , onChange: dispatch <?| E.inputText >>> unformatDateTime "YYYY-MM-DDTHH:mm" >>> hush >>> map DateTimeChanged
      }
  , H.div "form-check form-switch text-start mt-2"
      [ H.input_ "form-check-input"
          { type: "checkbox"
          , id: "arrival"
          , onChange: dispatch <| (E.inputChecked >>> ArriveByChanged)
          }
      , H.label_ "form-check-label" { htmlFor: "arrival" } [ H.text "arrival" ]
      ]
  , H.a_ "btn btn-primary mt-2"
      { href: fromMaybe "" do
          start <- state.departureBox.station
          destination <- state.arrivalBox.station
          dateTime <- state.dateTime
          pure $ toMotisWebUrl start destination dateTime state.arriveBy
      }
      "Search"
  ]

location :: SearchBox.Location -> Maybe SearchBox.Location
location = Just

noLocation :: Maybe SearchBox.Location
noLocation = Nothing

main :: String -> Maybe SearchBox.Location -> Maybe SearchBox.Location -> Effect Unit
main elementId from to = defaultMain { def: { init: (init from to), view, update }, elementId: elementId }
