import type { EngineInterface } from 'claude-code'

import { openApp } from '../health/app-client'
import { reasonOf } from '../error-display/failure-client'
import { projectPageUrl } from './board'
import { KANBAN } from '../health/server-health-client'

// /board readies the CDD Kanban as a press on it in the status row does: Python's App.open installs it while it is not
// installed, and this chat starts the board's server while it is not running, which stops when the chat ends.

// The board's address once it answers, readied first; a refusal says what failed and how to fix it.
export async function runningBoardUrl($: EngineInterface): Promise<string> {
  return (await openApp($, KANBAN)).url
}

// Where the board is, readied first, or what failed and how to fix it. The link names this chat's repository, so the
// page shows this chat's tickets whichever repository the server was started from.
export async function openedBoard($: EngineInterface): Promise<string> {
  try {
    return `The board is at ${await projectPageUrl($, await runningBoardUrl($))}.`
  } catch (failure) {
    return reasonOf(failure)
  }
}
