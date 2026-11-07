import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { toggleActionPicker } from './action-picker-client'
import { moveNext, type ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { chooseAction, reviewFidelity, runAction } from './fidelity-progress-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The canvas's glyph for each action a stage sends and for advance, the button's own move to the next stage; an action
// the canvas has no glyph for shows a dot.
const ACTION_ICONS: Record<string, string> = { generate: '✦', validate: '◎', review: '✓', satisfy: '✚', iterate: '↻', sketch: '✎', render: '⇄', document: '▭', advance: '→' }
const iconOf = (action: string): string => ACTION_ICONS[action] ?? '•'

// The action the button shows: advance once the stage is done, else the action fidelity's next action, or none.
export function actionOf(chatBar: ChatBarClient): string {
  return chatBar.canMoveNext ? 'advance' : (chatBar.actionFidelity?.nextAction ?? '')
}

// The action button runs what it shows: advance moves the session on, review records the person's approval, and every
// other action is a command the chat runs.
function pressAction($: EngineInterface, chatBar: ChatBarClient, action: string): unknown {
  const fidelity = chatBar.actionFidelity
  if (action === 'advance') return moveNext($, chatBar)
  if (!fidelity) return undefined
  return action === 'review' ? reviewFidelity($, fidelity) : runAction($, fidelity, action)
}

// The next action's icon, its action and fidelity on hover, and the ▾ that opens the picker.
export function ActionButtonView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar }: ChatBarDraw) {
  const action = actionOf(chatBar)
  if (!action) return null
  const target = action === 'advance' ? `move ${chatBar.sessionName} on` : `${action} ${chatBar.actionFidelity?.slug ?? ''}`
  return (
    <Box key="action" flexDirection="row" gap={0}>
      <Button key="next-action" plain label={target} onPress={() => pressAction($, chatBar, action)}>
        <Text color={BRAND.accent}>{iconOf(action)}</Text>
      </Button>
      <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{target}</Text>
      </Box>
      <Button key="action-picker" plain label="▾" onPress={() => toggleActionPicker($)} />
    </Box>
  )
}

// Every action the shown stage offers, the fidelity's next one marked, any of which runs in place of the next.
export function PickerView($: EngineInterface, { Box, Button }: ElementTable, { chatBar, picker }: ChatBarDraw) {
  const fidelity = chatBar.actionFidelity
  if (!picker.isOpen || !fidelity) return null
  return (
    <Box key="picker" flexDirection="row" gap={1} paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {chatBar.actions.map(action => (
        <Button key={`pick-${action}`} label={`${iconOf(action)} ${action}`} variant={action === fidelity.nextAction ? 'primary' : undefined} onPress={() => chooseAction($, fidelity, action)} />
      ))}
    </Box>
  )
}
