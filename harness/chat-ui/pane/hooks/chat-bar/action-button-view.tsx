import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { toggleActionPicker } from './action-picker-client'
import { moveNext, type ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { ACTION_ICONS, BUILDER_ACTIONS, chooseAction, reviewFidelity, runAction } from './fidelity-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

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

// The next action's icon and ▾, dark on an orange chip as the canvas draws them. A desktop ignores the colour of text
// inside a Button, so the chip is drawn text and its two Buttons, the action with its fidelity and the picker, sit on
// the card the chip reveals on hover.
export function ActionButtonView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar }: ChatBarDraw) {
  const action = actionOf(chatBar)
  if (!action) return null
  const target = action === 'advance' ? `move ${chatBar.sessionName} on` : `${action} ${chatBar.actionFidelity?.guidance ?? ''}`
  return (
    <Box key="action" flexDirection="row">
      <Box key="action-chip" flexDirection="row" gap={1} paddingX={1} backgroundColor={BRAND.accent}>
        <Text weight="bold" color={BRAND.ground}>{ACTION_ICONS[action] ?? '•'}</Text>
        <Text color={BRAND.ground}>▾</Text>
      </Box>
      <Box position="absolute" top={-1} left={0} flexDirection="row" gap={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Button key="next-action" plain label={target} onPress={() => pressAction($, chatBar, action)} />
        <Button key="action-picker" plain label="▾ another action" onPress={() => toggleActionPicker($)} />
      </Box>
    </Box>
  )
}

// Every builder action, the fidelity's next one marked, any of which runs in place of the next.
export function PickerView($: EngineInterface, { Box, Button }: ElementTable, { chatBar, picker }: ChatBarDraw) {
  const fidelity = chatBar.actionFidelity
  if (!picker.isOpen || !fidelity) return null
  return (
    <Box key="picker" flexDirection="column" alignSelf="flex-start" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {BUILDER_ACTIONS.map(action => (
        <Button key={`pick-${action}`} plain label={`${ACTION_ICONS[action]} ${action}${action === fidelity.nextAction ? '  (next)' : ''}`} onPress={() => chooseAction($, fidelity, action)} />
      ))}
    </Box>
  )
}
