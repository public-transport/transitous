{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchBox where

import Data.Bifunctor
import Data.Maybe (fromMaybe)
import Effect.Class (liftEffect)
import Elmish (Dispatch, ReactElement, Transition, forks, (<|))
import Elmish.HTML.Styled as H
import MotisForward (toMotisWebUrl)
import Prelude (pure, ($), (<<<), bind, discard)
import SearchField as SearchField

data Message
  = DepartureMsg SearchField.Message
  | ArrivalMsg SearchField.Message
  | Swap

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
update state Swap = do
  forks \{ dispatch } -> liftEffect do
    -- Swap departure and arrival state
    dispatch (DepartureMsg (SearchField.Swap state.arrivalBox))
    dispatch (ArrivalMsg (SearchField.Swap state.departureBox))

  pure state

view :: State -> Dispatch Message -> ReactElement
view state dispatch = H.div "text-end card-body p-4"
  [ H.div "row mb-3"
      [ SearchField.view state.departureBox (dispatch <<< DepartureMsg)
      , H.button_ "btn col-1 me-2" { onClick: dispatch <| Swap } [ H.i_ "bi bi-arrow-down-up pr-2" { title: "Swap" } "" ]
      ]
  , SearchField.view state.arrivalBox (dispatch <<< ArrivalMsg)
  , H.a_ "btn btn-primary mt-4 text-black"
      { href: fromMaybe "" do
          start <- state.departureBox.station
          destination <- state.arrivalBox.station
          pure $ toMotisWebUrl start destination
      }
      "Search"
  ]
