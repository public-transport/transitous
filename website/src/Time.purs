{-
SPDX-FileCopyrightText: 2025 Transitous contributors

SPDX-License-Identifier: AGPL-3.0-or-later
-}

module Time
  ( FormattedTimes
  , formatTimes
  ) where

import Prelude

import Data.Maybe (Maybe)
import Effect (Effect)

-- | A small helper record returned by 'formatTimes'.
-- | stopTime: Time formatted in the stop's local timezone (includes short tz name).
-- | userTime: Time formatted in the user's browser timezone (includes short tz name).
-- | showBoth: Whether stop timezone differs from browser timezone and both should be shown.
type FormattedTimes =
  { stopTime :: String
  , userTime :: String
  , showBoth :: Boolean
  }

-- | Format a UTC datetime string for display in both a stop-local timezone and the user's local timezone.
-- | Arguments:
-- |   utc: UTC datetime string (e.g. ISO-8601) returned by the API.
-- |   stopTz: Optional IANA timezone name for the stop (e.g. "Europe/Paris").
-- | Returns:
-- |   FormattedTimes: record containing stop-local time, user-local time, and whether both should be shown.
foreign import formatTimes :: String -> Maybe String -> Effect FormattedTimes
