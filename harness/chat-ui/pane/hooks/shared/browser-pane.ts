import type { EngineInterface } from 'claude-code'

import { reasonOf } from '../error-display/failure-client'

// The Claude desktop app's own browser pane, as /mcp lists it: its tool that opens a tab at a URL, its tabs with their
// origins, and the calls that move a tab and bring it to the front.
const BROWSER_PANE = 'Claude_Browser'
const OPEN_PANE_TAB = 'preview_start'
const TABS = 'tabs_context'
const SELECT_TAB = 'tabs_select'
const NAVIGATE = 'navigate'
// The desktop app's view of this chat, and its tool that shows a side pane, the browser pane being 'preview'.
const DESKTOP_VIEW = 'ccd_view'
const SHOW_PANE = 'show_pane'
const PREVIEW_PANE = 'preview'

type PaneTabs = { browserOpen: boolean; tabs: { tabId: string; origin: string; isActive: boolean }[] }
type McpAnswer = { isError?: boolean; content: { type: string; text?: string }[] }

// What an MCP answer says, its text blocks joined.
function saidBy(answer: McpAnswer): string {
  return answer.content.map(block => block.text ?? '').join(' ').trim()
}

// Opens a page in the Claude desktop app's browser pane, beside the chat, calling the pane's server directly: a tool call
// would go through the desktop's permission hooks, which refuse a plugin's call. A tab already on the page's origin is
// moved to the page and brought to the front rather than opening another. Returns why it did not open, empty once it
// did; it never opens the page anywhere else, so a pane that does not answer is seen and fixed.
export async function openInBrowserPane($: EngineInterface, url: string): Promise<string> {
  try {
    const why = await openedTab($, url)
    if (why) return why
    // A tab opens in the pane even while the pane is hidden, so the pane is then shown beside the chat.
    const shown = await $.mcp.call(DESKTOP_VIEW, SHOW_PANE, { pane: PREVIEW_PANE })
    return shown.isError ? `the tab opened, but ${DESKTOP_VIEW} ${SHOW_PANE} failed: ${saidBy(shown) || 'no reason given'}` : ''
  } catch (failure) {
    return `${BROWSER_PANE} could not be called: ${hookReasonOf(reasonOf(failure))}`
  }
}

async function openedTab($: EngineInterface, url: string): Promise<string> {
  const open = await tabOn($, new URL(url).origin)
  if (open) {
    const moved = await $.mcp.call(BROWSER_PANE, NAVIGATE, { url, tabId: open })
    if (moved.isError) return `${BROWSER_PANE} ${NAVIGATE} failed: ${saidBy(moved) || 'no reason given'}`
    const selected = await $.mcp.call(BROWSER_PANE, SELECT_TAB, { tabId: open })
    return selected.isError ? `${BROWSER_PANE} ${SELECT_TAB} failed: ${saidBy(selected) || 'no reason given'}` : ''
  }
  const opened = await $.mcp.call(BROWSER_PANE, OPEN_PANE_TAB, { url })
  const said = saidBy(opened)
  // The pane answers without isError when it opened a tab but the page did not load in it, saying "navOk": false.
  return opened.isError || /"navOk":\s*false/.test(said) ? `${BROWSER_PANE} ${OPEN_PANE_TAB} failed: ${said || 'no reason given'}` : ''
}

// The pane's tab on origin, the active one first; none while the pane is closed. A refused call or an answer that
// cannot be read throws, so openInBrowserPane says why. The answer is the tabs as JSON followed by a sentence about the
// pane, so the JSON is read up to its last brace.
async function tabOn($: EngineInterface, origin: string): Promise<string | null> {
  const answer = await $.mcp.call(BROWSER_PANE, TABS, {})
  const text = saidBy(answer)
  if (answer.isError) throw new Error(`${BROWSER_PANE} ${TABS} failed: ${text || 'no reason given'}`)
  let pane: PaneTabs
  try {
    pane = JSON.parse(text.slice(text.indexOf('{'), text.lastIndexOf('}') + 1)) as PaneTabs
  } catch (failure) {
    throw new Error(`${BROWSER_PANE} ${TABS} answered what is not its tabs (${reasonOf(failure)}): ${text || 'nothing'}`)
  }
  if (!pane.browserOpen) return null
  const onOrigin = pane.tabs.filter(tab => tab.origin === origin)
  return (onOrigin.find(tab => tab.isActive) ?? onOrigin[0])?.tabId ?? null
}

// The engine wraps a hook's refusal as "<plugin>: $.mcp.call(<server>, <tool>) refused: PreToolUse:<tool> hook error:
// <reason>", and a toast shows only its start, so the hook's own reason is put first, where the toast shows it.
const HOOK_REFUSAL = /^.*?refused:\s*PreToolUse:(\S+) hook error:\s*/s
function hookReasonOf(refusal: string): string {
  const wrapped = HOOK_REFUSAL.exec(refusal)
  return wrapped ? `${refusal.slice(wrapped[0].length)} (a PreToolUse hook on ${wrapped[1]})` : refusal
}
