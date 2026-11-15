import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { CommitData } from '@cdd/space/repo/repo'

import type { ToMainJson } from '../../types'
import { callTool, refreshChatBar } from '../chat-bar/chat-bar-client'
import { showFailure } from '../error-display/failure-client'

const PUSH_TOOL = 'repo.push_to_main'
const SHORT_SHA = 7

const toMain = atom({ plugin: 'cdd-board', key: 'toMain' } as const, { isAsking: false, state: 'idle', landed: null, error: null } as ToMainJson, { shape: 'to-main-2' })

// Mirrors the Python Repo for the chat bar's Push to main: whether the dialog is open, and how the last push went.
export class RepoClient {
  constructor(private readonly json: ToMainJson) {}

  get isAsking(): boolean {
    return this.json.isAsking
  }

  get state(): ToMainJson['state'] {
    return this.json.state
  }

  get error(): string | null {
    return this.json.error
  }

  // What the bar says once it is done, such as main at 1a2b3c4.
  get landed(): string {
    const commit = this.json.landed as CommitData | null
    return commit ? `main at ${commit.sha.slice(0, SHORT_SHA)}` : ''
  }
}

// Atom toMain, declared in pane/types/index.d.ts and kept in this file.
export async function currentRepo($: EngineInterface): Promise<RepoClient> {
  return new RepoClient(await read($, toMain))
}

export async function askToPush($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: true }))
}

export async function cancelPush($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: false }))
}

// Confirmed in the dialog: one call to repo.push_to_main for the folder this chat works in, then the board is read
// again so the bar shows the session as it now is.
export async function pushToMain($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: false, state: 'running', error: null }))
  try {
    const landed = await callTool<CommitData>($, PUSH_TOOL, {})
    await update($, toMain, json => ({ ...json, state: 'installed', landed }))
  } catch (failure) {
    await update($, toMain, json => ({ ...json, state: 'failed', error: String(failure) }))
    await showFailure($, 'The push to main failed', `Push to main on the chat bar, calling ${PUSH_TOOL}`, failure)
  }
  await refreshChatBar($)
}
