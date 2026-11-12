/**
 * What a `space/kanban/{sub_epic}.story.ui.spec.ts` file reaches the board app's Playwright setup through. Those files
 * sit beside the sub-epic's shared Python scenarios, outside this package, where `@playwright/test` cannot be resolved,
 * so the browser tier, its fixture project, and the Seed fixtures and page readings the sub-epics share come from here.
 */


import { expect, type Page } from '@playwright/test'

import { fixtureRoot, openSession, STAMP } from '../test-utils/fixture-repo'
import type { FakeChat } from './support'

export { expect, test } from '@playwright/test'
export type { Locator, Page } from '@playwright/test'

export * from './support'
export { STAMP, fixtureRoot, resetSessions, writeInto, writeSession } from '../test-utils/fixture-repo'

const CHAT_GONE_MILLISECONDS = 12_000
const CHAT_CHECKED_IN_MILLISECONDS = 10_000

// Seed: the lines Generate and Validate write to a session log on a fidelity, as fixture-repo.ts writes them.
export const generatedLine = (practice: string, fidelity: string, stamp = STAMP): string => `${stamp} generate /work ${practice} ${fidelity} markdown ${practice} no-chat`
export const validatedLine = (practiceClass: string, fidelity: string, stamp = STAMP): string => `${stamp} validate ${practiceClass} ${fidelity} no-chat`

// Seed: the session open in the fixture project, kept by the cdd server as Session.switch keeps it.
export function seedActive(ticket: string): void {
  openSession(fixtureRoot, ticket)
}

// What the chat was given, as the cdd-board mod took it at its check-ins.
export const receivedBy = (chat: FakeChat): string[] => chat.received.map(command => command.text)

// A chat that stopped checking in counts as gone only after a few seconds, so a page waits for the header to say so.
export async function waitForNoChat(page: Page): Promise<void> {
  await expect(page.getByText('No chat connected: load the cdd-board mod in a chat to send commands')).toBeVisible({ timeout: CHAT_GONE_MILLISECONDS })
}

// The board picks no chat on its own, since its list reorders as chats work, so the Person picks the one that checked in.
export async function waitForChat(page: Page, chat: FakeChat): Promise<void> {
  const picker = page.getByRole('combobox', { name: 'Chat to send commands to' })
  await expect(picker.locator(`option[value="${chat.id}"]`)).toBeAttached({ timeout: CHAT_CHECKED_IN_MILLISECONDS })
  await picker.selectOption(chat.id)
  await expect(picker).toHaveValue(chat.id)
}
