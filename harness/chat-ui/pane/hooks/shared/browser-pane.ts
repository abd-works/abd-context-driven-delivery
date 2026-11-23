import type { EngineInterface } from 'claude-code'

import { reasonOf } from './reason'

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

// Opens a page in the Claude desktop app's browser pane, beside the chat, calling the pane's server directly. A tab
// already on the page's origin is moved to the page and brought to the front rather than opening another. In auto mode
// Claude Desktop refuses the plugin's own call but runs the same call made by Claude, so the page is handed to Claude to
// open. Returns why it did not open, empty once it did or once Claude was asked; it never opens the page anywhere else,
// so a pane that does not answer is seen and fixed.
export async function openInBrowserPane($: EngineInterface, url: string): Promise<string> {
  try {
    const why = await openedTab($, url)
    if (why) return why
    // A tab opens in the pane even while the pane is hidden, so the pane is then shown beside the chat.
    const shown = await $.mcp.call(DESKTOP_VIEW, SHOW_PANE, { pane: PREVIEW_PANE })
    return shown.isError ? `the tab opened, but ${DESKTOP_VIEW} ${SHOW_PANE} failed: ${saidBy(shown) || 'no reason given'}` : ''
  } catch (failure) {
    const reason = reasonOf(failure)
    if (!AUTO_MODE_REFUSAL.test(reason)) return whyPaneNotCalled(reason)
    return handedToClaude($, url)
  }
}

// What Claude is asked when the pane refused the chat bar's own call in auto mode.
export function askedToOpen(url: string): string {
  return `Open ${url} in Claude's Browser pane beside this chat (${BROWSER_PANE} ${OPEN_PANE_TAB} with that url), then show the pane. The chat bar asked: in auto mode the pane refuses the bar's own call.`
}

// Claude asked to open url, empty once the chat took the request; a chat that dropped it, such as one in the middle of a
// turn, leaves the person the way to let the bar open pages itself.
async function handedToClaude($: EngineInterface, url: string): Promise<string> {
  const answer = await $.prompt.submit({ text: askedToOpen(url), asUser: true })
  return answer.drop === undefined ? '' : `${AUTO_MODE_ADVICE} (Claude was not asked to open it: the chat dropped the request, ${answer.drop || 'no reason given'}.)`
}

// What the person is told when the browser pane refused the call, from the refusal's own reason.
export function whyPaneNotCalled(reason: string): string {
  if (AUTO_MODE_REFUSAL.test(reason)) return AUTO_MODE_ADVICE
  return `${BROWSER_PANE} could not be called: ${hookReasonOf(reason)}`
}

// Claude Desktop's auto mode refuses a plugin's own call to the browser pane. The person can lift that by choosing
// another permission mode, so they are told where that choice is rather than shown the hook's wording.
const AUTO_MODE_REFUSAL = /in auto mode .* doesn't run this tool when a plugin's own code calls it/is
const AUTO_MODE_ADVICE =
  "Claude's Browser pane can't be opened from the chat bar while the chat is in Auto mode. " +
  'To let it open pages there, click the permission mode menu at the bottom of the chat box and choose Bypass permissions. ' +
  'Or ask Claude in the chat to open it for you.'

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
// pane, and that sentence can hold braces of its own (a closed pane's says to navigate with {"url": ...}), so only the
// first whole JSON object is read.
async function tabOn($: EngineInterface, origin: string): Promise<string | null> {
  const answer = await $.mcp.call(BROWSER_PANE, TABS, {})
  const text = saidBy(answer)
  if (answer.isError) throw new Error(`${BROWSER_PANE} ${TABS} failed: ${text || 'no reason given'}`)
  let pane: PaneTabs
  try {
    pane = JSON.parse(firstJsonObject(text)) as PaneTabs
  } catch (failure) {
    throw new Error(`${BROWSER_PANE} ${TABS} answered what is not its tabs (${reasonOf(failure)}): ${text || 'nothing'}`)
  }
  if (!pane.browserOpen) return null
  const onOrigin = pane.tabs.filter(tab => tab.origin === origin)
  return (onOrigin.find(tab => tab.isActive) ?? onOrigin[0])?.tabId ?? null
}

// The first JSON object in text, from its first brace to the brace that closes it, braces inside strings not counted.
// Text with no whole object answers what follows its first brace, which JSON.parse then refuses, saying why.
function firstJsonObject(text: string): string {
  const start = text.indexOf('{')
  let depth = 0
  let isInString = false
  for (let index = start; index >= 0 && index < text.length; index += 1) {
    const character = text[index]
    if (isInString) {
      if (character === '\\') index += 1
      else if (character === '"') isInString = false
    } else if (character === '"') isInString = true
    else if (character === '{') depth += 1
    else if (character === '}' && --depth === 0) return text.slice(start, index + 1)
  }
  return start < 0 ? text : text.slice(start)
}

// The engine wraps a hook's refusal as "<plugin>: $.mcp.call(<server>, <tool>) refused: PreToolUse:<tool> hook error:
// <reason>", and a toast shows only its start, so the hook's own reason is put first, where the toast shows it.
const HOOK_REFUSAL = /^.*?refused:\s*PreToolUse:(\S+) hook error:\s*/s
function hookReasonOf(refusal: string): string {
  const wrapped = HOOK_REFUSAL.exec(refusal)
  return wrapped ? `${refusal.slice(wrapped[0].length)} (a PreToolUse hook on ${wrapped[1]})` : refusal
}
