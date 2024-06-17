{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module Utils where

import Prelude

import Data.Array (length, zip, (..))
import Data.Maybe (Maybe(..))
import Data.Tuple (Tuple)

enumerate :: forall a. Array a -> Array (Tuple Int a)
enumerate xs = (zip (0 .. (length xs)) xs)

flatMap :: forall m a b. (Bind m) => (a -> m b) -> m a -> m b
flatMap = flip (>>=)

filterMaybe :: forall a. (a -> Boolean) -> Maybe a -> Maybe a
filterMaybe f m = m >>= (\v -> if f v then Just v else Nothing)
