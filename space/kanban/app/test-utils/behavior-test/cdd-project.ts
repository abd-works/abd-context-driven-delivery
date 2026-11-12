import { mkdtempSync } from 'node:fs'
import { rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { CddConnection } from '@cdd/cdd-connection'

import { createFixtureRepo, resetSessions } from '../fixture-repo'
import { runCheckoutPython } from './throwaway-cdd-home'

// Windows holds the folder for a moment after the server exits.
const REMOVE_RETRIES = 20
const REMOVE_RETRY_MILLISECONDS = 250
// Every behavior starts with this ticket open, as a chat that opened it leaves the sessions.
const FIRST_OPEN = 'checkout-flow'
// The open session as the cdd server keeps it, set through its own WorkState, for the project's folder: the page's calls
// name no chat. An empty name opens main.
const OPEN_SESSION = 'import sys; from space.work_state import WorkState; WorkState(sys.argv[1]).session = sys.argv[2]'

// A throwaway repository with no remote on the run's cdd server, so the server tier's moves and closes touch only this.
export class CddProject {
  readonly root = mkdtempSync(join(tmpdir(), 'cdd-board-server-tier-'))
  readonly cdd: CddConnection

  constructor() {
    createFixtureRepo(this.root)
    this.cdd = new CddConnection(this.root)
  }

  // A real tool really changes the sessions, so every behavior starts from the same ones, with the same one open.
  async reset(): Promise<void> {
    resetSessions(this.root)
    await this.open(FIRST_OPEN)
  }

  // Which session is open is kept by the cdd server in its home, never in the project; none opens main.
  async open(ticket: string | null): Promise<void> {
    runCheckoutPython('-c', OPEN_SESSION, this.root, ticket ?? '')
  }

  async close(): Promise<void> {
    await this.cdd.close()
    await rm(this.root, { recursive: true, force: true, maxRetries: REMOVE_RETRIES, retryDelay: REMOVE_RETRY_MILLISECONDS })
  }
}
