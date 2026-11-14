import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { HelpData } from '@cdd/space/kanban/board'

import type { FidelityHelpJson } from '../../types'
import { showFailure } from '../error-display/failure-client'
import { callTool } from './chat-bar-client'
import type { FidelityProgressClient } from './fidelity-progress-client'

// A fidelity's help in a pane of its own beside the chat: what the ? beside a practice on a board ticket shows, read
// from the same fidelity-progress.help, so the person reads it without leaving Claude.
export const HELP_PANE = 'cdd-help'
const fidelityHelp = atom({ plugin: 'cdd-board', key: 'fidelityHelp' } as const, null as FidelityHelpJson, { shape: 'fidelity-help-1' })

// Atom fidelityHelp, declared in pane/types/index.d.ts and kept in this file.
export function currentFidelityHelp($: EngineInterface) {
  return read($, fidelityHelp)
}

// The help as one markdown page, in the board help panel's order: the fidelity's overview, its guidance, then its rules.
// The overview's first heading names its section, which the page title already says, so it is left out.
function helpMarkdownOf(help: HelpData, name: string): string {
  const subject = help.fidelity ?? help.practice
  const overview = subject.overview.trim().replace(/^#+ .*\n+/, '')
  const rules = subject.rules.map(rule => `### ${rule.slug}\n\n${rule.body.trim()}`)
  return [
    `# ${name}`,
    `*${help.practice.short_name || help.practice.key} · ${help.stage?.name ?? 'Practice overview'}* · [on the forge](${help.href})`,
    overview,
    subject.guidance.trim() ? `## Guidance\n\n${subject.guidance.trim()}` : '',
    rules.length ? `## ${help.fidelity ? 'Rules' : 'Shared rules'}\n\n${rules.join('\n\n')}` : '',
  ].filter(Boolean).join('\n\n')
}

export async function openHelp($: EngineInterface, fidelity: FidelityProgressClient): Promise<void> {
  try {
    const help = await callTool<HelpData>($, 'fidelity-progress.help', { ticket: fidelity.progress.ticket.name, fidelity: fidelity.slug })
    await update($, fidelityHelp, () => ({ fidelity: fidelity.slug, markdown: helpMarkdownOf(help, fidelity.name) }))
    const opened = await $.ui.open({ id: HELP_PANE, title: `${fidelity.name} help` })
    if (!opened.isPlaced) $.ui.log(`cdd-board: the help pane waits to be placed: ${opened.reason}`, { to: 'debug' })
  } catch (failure) {
    await showFailure($, `The ${fidelity.slug} help did not open`, `Pressing the ${fidelity.slug} name above its dot, calling fidelity-progress.help`, failure)
  }
}

// The person closed the pane with its own mark: the help is forgotten, so the next open reads it afresh.
export async function forgetHelp($: EngineInterface): Promise<void> {
  await update($, fidelityHelp, () => null)
}
