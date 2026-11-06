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

// The orange chip of the canvas: the next action's icon, then the ▾ that opens the picker, its action and fidelity
// shown above it on hover.
export function ActionButtonView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar }: ChatBarDraw) {
  const action = actionOf(chatBar)
  if (!action) return null
  const target = action === 'advance' ? `move ${chatBar.sessionName} on` : `${action} ${chatBar.actionFidelity?.guidance ?? ''}`
  return (
    <Box key="action" flexDirection="row" gap={0}>
      <Button key="next-action" plain label={target} onPress={() => pressAction($, chatBar, action)}>
        <Text weight="bold" color={BRAND.onAccent} backgroundColor={BRAND.accent}>{` ${ACTION_ICONS[action] ?? '•'} `}</Text>
      </Button>
      <Button key="action-picker" plain label="▾" onPress={() => toggleActionPicker($)}>
        <Text color={BRAND.onAccent} backgroundColor={BRAND.accent}>▾</Text>
      </Button>
      <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{target}</Text>
      </Box>
    </Box>
  )
}

// Every builder action as a menu above the button: its icon, its name, and next beside the fidelity's next one. Any of
// them runs in place of the next.
export function PickerView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, picker }: ChatBarDraw) {
  const fidelity = chatBar.actionFidelity
  if (!picker.isOpen || !fidelity) return null
  return (
    <Box key="picker" flexDirection="column" alignSelf="flex-start" paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {BUILDER_ACTIONS.map(action => {
        const isNext = action === fidelity.nextAction
        return (
          <Button key={`pick-${action}`} plain label={action} onPress={() => chooseAction($, fidelity, action)}>
            <Text color={isNext ? BRAND.accent : BRAND.muted} backgroundColor={isNext ? BRAND.accentTint : undefined}>{`${ACTION_ICONS[action]} `}</Text>
            <Text color={isNext ? BRAND.text : BRAND.muted} backgroundColor={isNext ? BRAND.accentTint : undefined}>{action.padEnd(9)}</Text>
            <Text size="caption" color={BRAND.faint}>{isNext ? 'next' : ''}</Text>
          </Button>
        )
      })}
    </Box>
  )
}
