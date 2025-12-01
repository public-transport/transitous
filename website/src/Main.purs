{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module Main (main, location, noLocation) where

import Prelude (Unit, pure, ($), (<<<), bind)

import Elmish (Transition, Dispatch, ReactElement)
import Elmish.HTML.Styled as H
import Elmish.Boot (defaultMain)

import Effect (Effect)
import Data.Bifunctor
import Data.Maybe (fromMaybe, Maybe(..))

import SearchBox as SearchBox
import MotisForward (toMotisWebUrl)

data Message
  = DepartureMsg SearchBox.Message
  | ArrivalMsg SearchBox.Message

type State =
  { departureBox :: SearchBox.State
  , arrivalBox :: SearchBox.State
  }

init :: Maybe SearchBox.Location -> Maybe SearchBox.Location -> Transition Message State
init from to = do
  departureState <- lmap DepartureMsg $ SearchBox.init "Start" from
  arrivalState <- lmap ArrivalMsg $ SearchBox.init "Destination" to
  pure { departureBox: departureState, arrivalBox: arrivalState }

update :: State -> Message -> Transition Message State
update state (DepartureMsg msg) =
  bimap DepartureMsg state { departureBox = _ } $ SearchBox.update state.departureBox msg
update state (ArrivalMsg msg) =
  bimap ArrivalMsg state { arrivalBox = _ } $ SearchBox.update state.arrivalBox msg

view :: State -> Dispatch Message -> ReactElement
view state dispatch = H.div "text-end card-body p-4"
  [ SearchBox.view state.departureBox (dispatch <<< DepartureMsg)
  , SearchBox.view state.arrivalBox (dispatch <<< ArrivalMsg)
  , H.a_ "btn btn-primary mt-2"
      { href: fromMaybe "" do
          start <- state.departureBox.station
          destination <- state.arrivalBox.station
          pure $ toMotisWebUrl start destination
      }
      "Search"
  ]

location :: SearchBox.Location -> Maybe SearchBox.Location
location = Just

noLocation :: Maybe SearchBox.Location
noLocation = Nothing

main :: String -> Maybe SearchBox.Location -> Maybe SearchBox.Location -> Effect Unit
main elementId from to = defaultMain { def: { init: (init from to), view, update }, elementId: elementId }
