{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module SearchBox where

import Prelude

import Data.Argonaut.Decode (decodeJson, class DecodeJson)
import Data.Argonaut.Decode.Error (JsonDecodeError)
import Data.Argonaut.Decode.Parser (parseJson)
import Data.Array (length, zip, (..), (!!), null, nubBy, reverse)
import Data.DateTime (DateTime, diff)
import Data.Either (Either(..))
import Data.Foldable (find)
import Data.FormURLEncoded (fromArray, encode)
import Data.Maybe (Maybe(..), fromMaybe)
import Data.Time.Duration (Milliseconds(..))
import Data.Tuple (Tuple(..))
import Effect.Aff (Aff, delay)
import Effect.Class (liftEffect)
import Effect.Console (log)
import Effect.Now (nowDateTime)
import Elmish (Transition, Dispatch, ReactElement, (<|), (<?|))
import Elmish.Component (fork, forkMaybe)
import Elmish.HTML.Events as E
import Elmish.HTML.Styled as H
import Fetch (fetch)

type Area = { name :: String, adminLevel :: Int }
type Location =
  { type :: String
  , id :: String
  , tokens :: Array (Array Int)
  , name :: String
  , lat :: Number
  , lon :: Number
  , areas :: Array Area
  , level :: Int
  , zip :: Maybe String
  , score :: Number
  }

motisInstance :: String
motisInstance = "https://europe.motis-project.de"

getCity :: Array Area -> Maybe String
getCity areas =
  areas
    # find (\r -> r.adminLevel <= 8)
    # map (_.name)

getCountry :: Array Area -> Maybe String
getCountry areas =
  areas
    # find (\r -> r.adminLevel == 2)
    # map (_.name)

getRegion :: Location -> Maybe String
getRegion address = do
  let areas = reverse $ address.areas
  city <- getCity areas
  country <- getCountry areas
  Just $ city <> ", " <> country

uniqueLocations :: Array Location -> Array Location
uniqueLocations = nubBy (\a b -> compare (a.name <> fromMaybe "" (getRegion a)) (b.name <> fromMaybe "" (getRegion b)))

parseMotisResponse :: forall a. DecodeJson a => String -> Either JsonDecodeError a
parseMotisResponse text = do
  decoded <- parseJson text
  decodeJson decoded

data Message
  = SearchChanged String
  | GotResults (Array Location)
  | ShowSuggestions Boolean
  | Select Location
  | NewInput DateTime
  | StartGuessRequest String
  | SelectionUp
  | SelectionDown

type State =
  { entries :: Array Location
  , showSuggestions :: Boolean
  , station :: Maybe Location
  , query :: String
  , placeholderText :: String
  , lastRequestTime :: Maybe DateTime
  , currentlySelectedIndex :: Int
  }

debounceDelay :: Milliseconds
debounceDelay = Milliseconds 150.0

logAff :: String -> Aff Unit
logAff = log >>> liftEffect

requestGuesses :: String -> Aff (Array Location)
requestGuesses query = do
  { status, statusText, text } <- fetch
    ( motisInstance <> "/api/v1/geocode?" <>
        ( fromMaybe "" $ encode $ fromArray
            [ Tuple "text" (Just query) ]
        )
    )
    { headers: { "Accept": "application/json" } }
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
      Right response -> pure response

requestGuessesDebounced :: State -> String -> Transition Message State
requestGuessesDebounced state query =
  case state.lastRequestTime of
    Just lastRequestTime -> do
      forkMaybe do
        now <- liftEffect nowDateTime
        if diff now lastRequestTime > debounceDelay then do
          guesses <- requestGuesses query
          pure $ Just (GotResults (uniqueLocations guesses))
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
          Just guess -> guess.name
          Nothing -> state.query
      }
  , case state.showSuggestions && not (null state.entries) of
      true -> H.ul "dropdown-menu show" suggestionEntries
      false -> H.ul "dropdown-menu" suggestionEntries
  ]
  where
  suggestionEntries =
    map
      ( \(Tuple i location) ->
          if i == state.currentlySelectedIndex then H.li_ "dropdown-item dropdown-item-active cursor-shape-pointer"
            { onClick: dispatch <| Select location, autoFocus: true }
            [ H.i
                case location.type of
                  "STOP" -> "bi-train-front-fill"
                  _ -> "bi-geo-alt-fill"
                ""
            , H.span "p-2" location.name
            , H.span "text-secondary text-xs" (fromMaybe "" $ getRegion location)
            ]
          else H.li_ "dropdown-item cursor-shape-pointer"
            { onClick: dispatch <| Select location }
            [ H.i
                case location.type of
                  "STOP" -> "bi-train-front-fill"
                  _ -> "bi-geo-alt-fill"
                ""
            , H.span "p-2" location.name
            , H.span "text-secondary text-xs" (fromMaybe "" $ getRegion location)
            ]
      )
      (zip (0 .. (length state.entries)) state.entries)
