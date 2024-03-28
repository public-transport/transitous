{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchBox where

import Prelude

import Elmish (Transition, Dispatch, ReactElement, (<|), (<?|))
import Elmish.HTML.Events as E
import Elmish.HTML.Styled as H
import Elmish.Component (fork, forkMaybe)

import Data.Either (Either(..))
import Data.Array (length, zip, (..), (!!))
import Data.Maybe (Maybe(..))
import Data.Tuple (Tuple(..))
import Effect.Class (liftEffect)
import Effect.Console (log)
import Effect.Aff (Aff, delay)

import Data.Argonaut.Decode (decodeJson)
import Data.Argonaut.Decode.Parser (parseJson)
import Data.Argonaut.Decode.Error (JsonDecodeError)
import Data.Argonaut.Encode (toJsonString)

import Fetch (Method(..), fetch)

import Effect.Now (nowDateTime)

import Data.DateTime (DateTime, diff)
import Data.Time.Duration (Milliseconds(..))

-- Requests
type StationGuesserRequest = { input :: String, guess_count :: Int }
type MotisRequest = { content_type :: String, content :: StationGuesserRequest, destination :: { type :: String, target :: String } }

serializeMotisRequest :: MotisRequest -> String
serializeMotisRequest = toJsonString

guessRequest :: String -> String
guessRequest text = serializeMotisRequest
  { content_type: "StationGuesserRequest"
  , destination:
      { type: "Module"
      , target: "/guesser"
      }
  , content:
      { input: text
      , guess_count: 10
      }
  }

-- Response
type Position = { lat :: Number, lng :: Number }
type Station = { id :: String, name :: String, pos :: Position }
type StationResponse = { content :: { guesses :: Array Station } }

parseMotisResponse :: String -> Either JsonDecodeError StationResponse
parseMotisResponse text = do
  decoded <- parseJson text
  decodeJson decoded

data Message
  = SearchChanged String
  | GotResults (Array Station)
  | ShowSuggestions Boolean
  | Select Station
  | NewInput DateTime
  | StartGuessRequest String
  | SelectionUp
  | SelectionDown

type State =
  { entries :: Array Station
  , showSuggestions :: Boolean
  , station :: Maybe Station
  , query :: String
  , placeholderText :: String
  , lastRequestTime :: Maybe DateTime
  , currentlySelectedIndex :: Int
  }

debounceDelay :: Milliseconds
debounceDelay = Milliseconds 150.0

requestGuesses :: String -> Aff (Array Station)
requestGuesses query = do
  let requestUrl = "https://routing.spline.de/api/"
  { status, statusText, text } <- fetch requestUrl
    { method: POST
    , headers: { "Content-Type": "application/json" }
    , body: guessRequest query
    }
  responseBody <- text

  if status /= 200 then do
    logAff (statusText <> responseBody)
    pure []
  else do
    let result = parseMotisResponse responseBody
    case result of
      Left err -> do
        logAff (show err)
        pure []
      Right response -> pure (response.content.guesses)
  where
  logAff = log >>> liftEffect

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
          Just { name } -> name
          Nothing -> state.query
      }
  , if state.showSuggestions && (length state.entries) > 0 then H.ul "dropdown-menu show" $ suggestionEntries
    else H.ul "dropdown-menu" $ suggestionEntries
  ]
  where
  suggestionEntries =
    map
      ( \(Tuple i { name, id, pos }) ->
          if i == state.currentlySelectedIndex then H.li_ "dropdown-item dropdown-item-active cursor-shape-pointer"
            { onClick: dispatch <| Select { name, id, pos }, autoFocus: true }
            name
          else H.li_ "dropdown-item cursor-shape-pointer"
            { onClick: dispatch <| Select { name, id, pos } }
            name
      )
      (zip (0 .. (length state.entries)) state.entries)
