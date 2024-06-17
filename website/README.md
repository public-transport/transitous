<!--
SPDX-FileCopyrightText: 2024 Jonah Brüchert <jbb@kaidan.im>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Website

## Development Setup

**Prerequisites**:
 * hugo (only the extended version is tested at this point)
 * npm

```sh
git submodule update --init --checkout
npm install
npm run start
```

All hugo content fill be automatically rebuilt on the fly, but a restart is still needed to rebuild the purescript files.

## Release builds

```sh
npm run release
```

The output will be placed in `public/`.
