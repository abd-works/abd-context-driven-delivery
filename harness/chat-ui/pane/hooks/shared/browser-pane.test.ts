// Why a page did not open in Claude's Browser pane, as the chat bar tells the person.
import { expect, test } from 'claude-code/testing'

import { whyPaneNotCalled } from './browser-pane'

// Interaction: Claude Desktop's refusal of a plugin's own call to the browser pane while the chat is in auto mode.
const AUTO_MODE_REFUSAL =
  "cdd-chat-ui: $.mcp.call(Claude_Browser, tabs_context) refused: PreToolUse:mcp__Claude_Browser__tabs_context hook error: " +
  "Not run: in auto mode Claude Desktop doesn't run this tool when a plugin's own code calls it. Have Claude make the call."

test('a page refused in auto mode tells the person to choose Bypass permissions at the bottom of the chat box', () => {
  expect(whyPaneNotCalled(AUTO_MODE_REFUSAL)).toContain('click the permission mode menu at the bottom of the chat box and choose Bypass permissions')
})
