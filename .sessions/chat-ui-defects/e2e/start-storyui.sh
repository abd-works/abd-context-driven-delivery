#!/bin/sh
# Starts Story UI for e2e: the in-memory API (serve-dev.ts, no MongoDB) on 3021 and Vite on 5193.
export PATH="/usr/bin:/mingw64/bin:$PATH"
cd /c/dev/story-ui || exit 1
PORT=3021 node ./node_modules/tsx/dist/cli.mjs packages/story-map-workspace/serve-dev.ts &
exec node ./node_modules/vite/bin/vite.js --config ../abd-context-driven-delivery/.sessions/chat-ui-defects/e2e/storyui-vite.config.mjs
