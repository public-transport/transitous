{-
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-}

{-
Welcome to a Spago project!
You can edit this file as you like.

Need help? See the following resources:
- Spago documentation: https://github.com/purescript/spago
- Dhall language tour: https://docs.dhall-lang.org/tutorials/Language-Tour.html
-}
{ name = "my-project"
, dependencies =
  [ "aff"
  , "argonaut-codecs"
  , "arrays"
  , "bifunctors"
  , "console"
  , "control"
  , "datetime"
  , "effect"
  , "either"
  , "elmish"
  , "elmish-html"
  , "enums"
  , "fetch"
  , "foldable-traversable"
  , "form-urlencoded"
  , "integers"
  , "maybe"
  , "now"
  , "prelude"
  , "strings"
  , "tuples"
  , "web-html"
  , "web-url"
  ]
, packages = ./packages.dhall
, sources = [ "src/**/*.purs" ]
}
