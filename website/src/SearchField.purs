{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchField where

import Prelude (bind, compare, discard, map, mod, negate, not, pure, (#), ($), (&&), (+), (-), (<=), (<>), (==), (>), (>>>))

import Elmish (Transition, Dispatch, ReactElement, (<|), (<?|))
import Elmish.HTML.Events as E
import Elmish.HTML.Styled as H
import Elmish.Component (fork, forkMaybe)

import Data.Array (length, zip, (..), (!!), null, nubBy)
import Data.Maybe (Maybe(..), fromMaybe)
import Data.Tuple (Tuple(..))
import Data.Foldable (find)
import Effect.Class (liftEffect)
import Effect.Aff (Aff, delay)

import Effect.Now (nowDateTime)

import Data.DateTime (DateTime, diff)
import Data.Time.Duration (Milliseconds(..))

import Motis (Address, Station, sendAddressRequest, sendStationRequest)

data Guess = StationGuess Station | AddressGuess Address

getCity :: Address -> Maybe String
getCity address =
  address.regions
    # find (\r -> r.admin_level <= 8)
    # map (_.name)

getCountry :: Address -> Maybe String
getCountry address =
  address.regions
    # find (\r -> r.admin_level == 2)
    # map (_.name)

getRegion :: Address -> Maybe String
getRegion address = do
  city <- getCity address
  country <- getCountry address
  Just $ city <> ", " <> country

uniqueAddresses :: Array Address -> Array Address
uniqueAddresses = nubBy (\a b -> compare (getRegion a) (getRegion b))

data Message
  = SearchChanged String
  | GotResults (Array Guess)
  | ShowSuggestions Boolean
  | Select Guess
  | NewInput DateTime
  | StartGuessRequest String
  | SelectionUp
  | SelectionDown

type State =
  { entries :: Array Guess
  , showSuggestions :: Boolean
  , station :: Maybe Guess
  , query :: String
  , placeholderText :: String
  , lastRequestTime :: Maybe DateTime
  , currentlySelectedIndex :: Int
  }

debounceDelay :: Milliseconds
debounceDelay = Milliseconds 150.0

requestGuesses :: String -> Aff (Array Guess)
requestGuesses query = do
  stationResponse <- sendStationRequest query
  addressResponse <- sendAddressRequest query
  pure $ fromMaybe [] do
    sr <- stationResponse
    ar <- addressResponse
    Just $ map StationGuess sr.guesses <> map AddressGuess (uniqueAddresses ar.guesses)

requestGuessesDebounced :: State -> String -> Transition Message State
requestGuessesDebounced state query =
  case state.lastRequestTime of
    Just lastRequestTime -> do
      forkMaybe do
        now <- liftEffect nowDateTime
        if diff now lastRequestTime > debounceDelay then do
          guesses <- requestGuesses query
          pure $ Just (GotResults guesses)
        else pure Nothing
      pure state
    Nothing -> pure state

onSearchChanged :: State -> String -> Transition Message State
onSearchChanged state query = do
  -- Update debounce timer
  fork do
    now <- liftEffect nowDateTime
    pure (NewInput now)

  -- Start request after delay
  fork do
    delay debounceDelay
    pure (StartGuessRequest query)

  pure state { query = query, station = Nothing }

init :: String -> Transition Message State
init placeholderText = pure
  { entries: []
  , showSuggestions: false
  , station: Nothing
  , query: ""
  , placeholderText: placeholderText
  , lastRequestTime: Nothing
  , currentlySelectedIndex: -1
  }

update :: State -> Message -> Transition Message State
update state (SearchChanged query) = onSearchChanged state query
update state (GotResults results) = pure state { entries = results }
update state (ShowSuggestions s) = pure state { showSuggestions = s }
update state (Select station) = pure state { showSuggestions = false, station = Just station }
update state (NewInput time) = pure state { lastRequestTime = Just time }
update state (StartGuessRequest query) = requestGuessesDebounced state query
update state SelectionUp = pure state { currentlySelectedIndex = (state.currentlySelectedIndex - 1) `mod` (length state.entries) }
update state SelectionDown = pure state { currentlySelectedIndex = (state.currentlySelectedIndex + 1) `mod` (length state.entries) }

view :: State -> Dispatch Message -> ReactElement
view state dispatch = H.div "mb-3"
  [ H.input_ "form-control mb-2"
      { onChange: dispatch <| E.inputText >>> SearchChanged
      , onFocus: dispatch <| ShowSuggestions true
      , placeholder: state.placeholderText
      , onKeyUp: dispatch <?| \(E.KeyboardEvent event) -> case event.key of
          "ArrowUp" -> Just SelectionUp
          "ArrowDown" -> Just SelectionDown
          "Enter" -> do
            station <- state.entries !! state.currentlySelectedIndex
            pure $ Select station
          _ -> Nothing
      , value: case state.station of
          Just guess -> case guess of
            StationGuess { name } -> name
            AddressGuess { name } -> name
          Nothing -> state.query
      }
  , case state.showSuggestions && not (null state.entries) of
      true -> H.ul "dropdown-menu show" suggestionEntries
      false -> H.ul "dropdown-menu" suggestionEntries
  ]
  where
  suggestionEntries =
    map
      ( \(Tuple i guess) ->
          case guess of
            StationGuess station -> do
              if i == state.currentlySelectedIndex then H.li_ "dropdown-item dropdown-item-active cursor-shape-pointer"
                { onClick: dispatch <| Select (StationGuess station), autoFocus: true }
                [ H.i "bi bi-train-front-fill" ""
                , H.span "p-2" (station.name)
                ]
              else H.li_ "dropdown-item cursor-shape-pointer"
                { onClick: dispatch <| Select (StationGuess station) }
                [ H.i "bi bi-train-front-fill" ""
                , H.span "p-2" (station.name)
                ]
            AddressGuess address -> do
              if i == state.currentlySelectedIndex then H.li_ "dropdown-item dropdown-item-active cursor-shape-pointer"
                { onClick: dispatch <| Select (AddressGuess address), autoFocus: true }
                [ H.i "bi bi-geo-alt-fill" ""
                , H.span "p-2" address.name
                , H.span "text-secondary text-xs" (fromMaybe "" $ getRegion address)
                ]
              else H.li_ "dropdown-item cursor-shape-pointer"
                { onClick: dispatch <| Select (AddressGuess address) }
                [ H.i "bi bi-geo-alt-fill" ""
                , H.span "p-2" address.name
                , H.span "text-secondary text-xs" (fromMaybe "" $ getRegion address)
                ]
      )
      (zip (0 .. (length state.entries)) state.entries)
