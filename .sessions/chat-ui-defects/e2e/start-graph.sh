#!/bin/sh
# Starts the knowledge graph app for e2e: its API server on 3010 and Vite on 5183, against the sandbox project.
export PATH="/usr/bin:/mingw64/bin:$PATH"
cd /c/dev/abd-context-driven-delivery/harness/graph/app || exit 1
export GRAPH_PROJECT='C:\Users\jeffa\AppData\Local\Temp\claude\C--dev-abd-context-driven-delivery\a69aa582-a698-4740-b239-eafa8158a45b\scratchpad\board-sandbox'
PORT=3010 node ./node_modules/tsx/dist/cli.mjs server.ts &
exec node ./node_modules/vite/bin/vite.js --config ../../../.sessions/chat-ui-defects/e2e/graph-vite.config.mjs
