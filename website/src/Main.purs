{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module Main where

import Effect (Effect)
import Data.Unit (Unit)
import Elmish.Boot (defaultMain)

import SearchBox as SearchBox
import SearchResults as SearchResults

searchBoxMain :: Effect Unit
searchBoxMain = defaultMain { def: { init: SearchBox.init, view: SearchBox.view, update: SearchBox.update }, elementId: "searchbox" }

searchResultsMain :: Effect Unit
searchResultsMain = defaultMain { def: { init: SearchResults.init, view: SearchResults.view, update: SearchResults.update }, elementId: "searchresults" }
