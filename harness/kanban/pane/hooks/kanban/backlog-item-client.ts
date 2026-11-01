import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BacklogDraftJson, BacklogItemJson } from '../../types'
import { callTool, itemAddress, refresh } from './board-client'

const EMPTY_DRAFT: BacklogDraftJson = { isOpen: false, title: '', text: '' }

const backlogDraft = atom({ plugin: 'cdd-board', key: 'backlogDraft' } as const, EMPTY_DRAFT)

// Mirrors the Python BacklogItem for display.
export class BacklogItemClient {
  constructor(private readonly json: BacklogItemJson) {}

  get title(): string {
    return this.json.title
  }

  get text(): string {
    return this.json.text
  }

  get path(): string {
    return this.json.path
  }

  get lastActivity(): string {
    return this.json.last_activity
  }

  get address(): string {
    return itemAddress(this.json)
  }
}

export async function start($: EngineInterface, item: BacklogItemClient): Promise<void> {
  await callTool($, 'backlog-item.start', { backlog_item: item.title })
  await refresh($)
}

export function currentDraft($: EngineInterface) {
  return read($, backlogDraft)
}

export function openDraft($: EngineInterface) {
  return update($, backlogDraft, draft => ({ ...draft, isOpen: true }))
}

export function cancelDraft($: EngineInterface) {
  return update($, backlogDraft, () => EMPTY_DRAFT)
}

export function typeDraftTitle($: EngineInterface, title: string) {
  return update($, backlogDraft, draft => ({ ...draft, title }))
}

export function typeDraftText($: EngineInterface, text: string) {
  return update($, backlogDraft, draft => ({ ...draft, text }))
}

export async function add($: EngineInterface, draft: BacklogDraftJson): Promise<void> {
  await update($, backlogDraft, () => EMPTY_DRAFT)
  await callTool($, 'backlog-item.add', { title: draft.title.trim(), text: draft.text.trim() })
  await refresh($)
}
