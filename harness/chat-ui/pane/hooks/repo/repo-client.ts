import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { CommitData } from '@cdd/space/repo/repo'

import type { ToMainJson } from '../../types'
import { callTool, refreshChatBar } from '../chat-bar/chat-bar-client'
import { showFailure } from '../error-display/failure-client'

// What taking a session's work to main does: merge it into main in the clone, or push it to main on origin.
export type ToMain = 'merge' | 'push'

const TOOLS: Record<ToMain, string> = { merge: 'repo.merge_to_main', push: 'repo.push_to_main' }
const SHORT_SHA = 7

const toMain = atom({ plugin: 'cdd-board', key: 'toMain' } as const, { asking: null, state: 'idle', landed: null, error: null } as ToMainJson)

// Mirrors the Python Repo for the chat bar's Merge to main and Push to main: which one the dialog asks about, and how
// the last one went.
export class RepoClient {
  constructor(private readonly json: ToMainJson) {}

  get asking(): ToMain | null {
    return this.json.asking
  }

  get state(): ToMainJson['state'] {
    return this.json.state
  }

  get error(): string | null {
    return this.json.error
  }

  // What the bar says once it is done, such as merged into main at 1a2b3c4.
  get landed(): string {
    const commit = this.json.landed as CommitData | null
    return commit ? `main at ${commit.sha.slice(0, SHORT_SHA)}` : ''
  }
}

// Atom toMain, declared in pane/types/index.d.ts and kept in this file.
export async function currentRepo($: EngineInterface): Promise<RepoClient> {
  return new RepoClient(await read($, toMain))
}

export async function askToMain($: EngineInterface, asking: ToMain): Promise<void> {
  await update($, toMain, json => ({ ...json, asking }))
}

export async function cancelToMain($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, asking: null }))
}

// Confirmed in the dialog: one call to repo.merge_to_main or repo.push_to_main for the folder this chat works in, then
// the board is read again so the bar shows the session as it now is.
export async function takeToMain($: EngineInterface, taking: ToMain): Promise<void> {
  await update($, toMain, json => ({ ...json, asking: null, state: 'running', error: null }))
  try {
    const landed = await callTool<CommitData>($, TOOLS[taking], {})
    await update($, toMain, json => ({ ...json, state: 'installed', landed }))
  } catch (failure) {
    await update($, toMain, json => ({ ...json, state: 'failed', error: String(failure) }))
    await showFailure($, taking === 'merge' ? 'The merge into main failed' : 'The push to main failed', `${taking === 'merge' ? 'Merge' : 'Push'} to main on the chat bar, calling ${TOOLS[taking]}`, failure)
  }
  await refreshChatBar($)
}
