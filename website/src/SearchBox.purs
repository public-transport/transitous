{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchBox where


import Prelude (pure, ($), (<<<), bind)

import Elmish (Transition, Dispatch, ReactElement)
import Elmish.HTML.Styled as H

import Data.Bifunctor
import Data.Maybe (fromMaybe)

import SearchField as SearchField
import MotisForward (toMotisWebUrl)

data Message
  = DepartureMsg SearchField.Message
  | ArrivalMsg SearchField.Message

type State =
  { departureBox :: SearchField.State
  , arrivalBox :: SearchField.State
  }

init :: Transition Message State
init = do
  departureState <- lmap DepartureMsg $ SearchField.init "Start"
  arrivalState <- lmap ArrivalMsg $ SearchField.init "Destination"
  pure { departureBox: departureState, arrivalBox: arrivalState }

update :: State -> Message -> Transition Message State
update state (DepartureMsg msg) =
  bimap DepartureMsg state { departureBox = _ } $ SearchField.update state.departureBox msg
update state (ArrivalMsg msg) =
  bimap ArrivalMsg state { arrivalBox = _ } $ SearchField.update state.arrivalBox msg

view :: State -> Dispatch Message -> ReactElement
view state dispatch = H.div "text-end card-body p-4"
  [ SearchField.view state.departureBox (dispatch <<< DepartureMsg)
  , SearchField.view state.arrivalBox (dispatch <<< ArrivalMsg)
  , H.a_ "btn btn-primary mt-2"
      { href: fromMaybe "" do
          start <- state.departureBox.station
          destination <- state.arrivalBox.station
          pure $ toMotisWebUrl start destination
      }
      "Search"
  ]
