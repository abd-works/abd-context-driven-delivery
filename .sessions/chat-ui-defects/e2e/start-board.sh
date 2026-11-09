#!/bin/sh
# Starts the e2e sandbox Session Board (see serve-board-sandbox.ts).
export PATH="/usr/bin:/mingw64/bin:$PATH"
cd /c/dev/abd-context-driven-delivery/space/kanban/app || exit 1
export BOARD_PORT=8790
export BOARD_PROJECT='C:\Users\jeffa\AppData\Local\Temp\claude\C--dev-abd-context-driven-delivery\a69aa582-a698-4740-b239-eafa8158a45b\scratchpad\board-sandbox'
export BOARD_DIST='C:\dev\abd-context-driven-delivery\.sessions\chat-ui-defects\e2e\board-dist'
exec node ./node_modules/tsx/dist/cli.mjs ../../../.sessions/chat-ui-defects/e2e/serve-board-sandbox.ts
