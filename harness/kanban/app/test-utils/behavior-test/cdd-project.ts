import { mkdtempSync } from 'node:fs'
import { rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { CddConnectionNode, locateCdd } from '@src/cdd/cdd-connection-node'

import { createFixtureRepo, resetSessions } from '../fixture-repo'

const SOURCE_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..', '..')
// Windows holds the folder for a moment after the server exits.
const REMOVE_RETRIES = 20
const REMOVE_RETRY_MILLISECONDS = 250

// A throwaway repository with no remote and a real cdd server on it, so the server tier's moves and closes touch only this.
export class CddProject {
  readonly root = mkdtempSync(join(tmpdir(), 'cdd-board-server-tier-'))
  readonly cdd: CddConnectionNode

  constructor() {
    createFixtureRepo(this.root)
    this.cdd = new CddConnectionNode(locateCdd(SOURCE_ROOT, { ...process.env, BOARD_PROJECT: this.root }))
  }

  // A real tool really changes the sessions, so every behavior starts from the same ones.
  reset(): void {
    resetSessions(this.root)
  }

  async close(): Promise<void> {
    await this.cdd.close()
    await rm(this.root, { recursive: true, force: true, maxRetries: REMOVE_RETRIES, retryDelay: REMOVE_RETRY_MILLISECONDS })
  }
}
