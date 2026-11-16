import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ToMainJson } from '../../types'
import { callTool, currentChatBar, refreshChatBar } from '../chat-bar/chat-bar-client'
import { shownAsFailure } from '../error-display/failure-client'

// Where a push lands: the session's own branch, or merged into main on origin.
export type PushTarget = 'branch' | 'main'

const TOOLS: Record<PushTarget, string> = { branch: 'repo.push_work', main: 'repo.push_to_main' }
const PRESSED: Record<PushTarget, string> = { branch: 'Push on the chat bar', main: 'Push & merge to origin/main on the chat bar' }
const FAILED: Record<PushTarget, string> = { branch: 'The push failed', main: 'The push to main failed' }

const toMain = atom({ plugin: 'cdd-board', key: 'toMain' } as const, { isAsking: false, state: 'idle', error: null } as ToMainJson, { shape: 'to-main-4' })

// Mirrors the Python Repo for the chat bar's two pushes: whether Push to main's dialog is open, and how the last push went.
export class RepoClient {
  constructor(
    private readonly json: ToMainJson,
    readonly session: string,
  ) {}

  get isAsking(): boolean {
    return this.json.isAsking
  }

  get state(): ToMainJson['state'] {
    return this.json.state
  }

  get error(): string | null {
    return this.json.error
  }
}

// Atom toMain, declared in pane/types/index.d.ts and kept in this file. The session the pushes carry is named as the
// chat bar names it: its title, else its ticket's name.
export async function currentRepo($: EngineInterface): Promise<RepoClient> {
  const chatBar = await currentChatBar($)
  return new RepoClient(await read($, toMain), chatBar.title || chatBar.sessionName)
}

export async function askToPush($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: true }))
}

export async function cancelPush($: EngineInterface): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: false }))
}

// Push: one call to repo.push_work for the folder this chat works in, its branch pushed and nothing merged.
export async function pushWork($: EngineInterface): Promise<void> {
  await pushTo($, 'branch')
}

// Confirmed in the dialog: one call to repo.push_to_main for the folder this chat works in.
export async function pushToMain($: EngineInterface): Promise<void> {
  await pushTo($, 'main')
}

// The one call both pushes share; then the board is read again so the bar shows the session as it now is.
async function pushTo($: EngineInterface, target: PushTarget): Promise<void> {
  await update($, toMain, json => ({ ...json, isAsking: false, state: 'running', error: null }))
  try {
    await callTool<object>($, TOOLS[target], {})
    await update($, toMain, json => ({ ...json, state: 'installed' }))
  } catch (failure) {
    await update($, toMain, json => ({ ...json, state: 'failed', error: String(failure) }))
    await shownAsFailure($, FAILED[target], `${PRESSED[target]}, calling ${TOOLS[target]}`)(failure)
  }
  await refreshChatBar($)
}
