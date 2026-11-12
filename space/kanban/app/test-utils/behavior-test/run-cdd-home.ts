import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { ThrowawayCddHome } from './throwaway-cdd-home'

const CHAT_ID_VARIABLE = 'CLAUDE_CODE_SESSION_ID'

// Vitest's global setup: one cdd server for the whole run, serving this checkout, with chats kept apart from the
// person's real ones. Spec files run one after another on it, and the run stops it at the end.
export default function startRunCddHome(): () => void {
  const chats = mkdtempSync(join(tmpdir(), 'cdd-board-run-chats-'))
  process.env.CDD_CHATS_FOLDER = join(chats, 'chats')
  process.env.CLAUDE_CONFIG_DIR = chats
  // The connect script names the chat a call comes from by this variable; a run started from a chat would otherwise
  // answer as that chat, and keep its open sessions under that chat's entry instead of the project's.
  delete process.env[CHAT_ID_VARIABLE]
  const home = ThrowawayCddHome.forRun()
  return () => {
    home.close()
    rmSync(chats, { recursive: true, force: true })
  }
}
