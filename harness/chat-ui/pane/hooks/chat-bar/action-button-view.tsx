import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { GlyphButtonView } from '../glyph-button-view'
import { chooseAction, clearChosenAction, toggleActionPicker } from './action-picker-client'
import { moveNext, type ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { ACTION_ICONS, BUILDER_ACTIONS, openBoard, reviewFidelity, runAction } from './fidelity-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The action the button shows: advance once the stage is done, else the action fidelity's next action, or none.
export function actionOf(chatBar: ChatBarClient): string {
  return chatBar.canMoveNext ? 'advance' : (chatBar.actionFidelity?.nextAction ?? '')
}

// What the button shows and runs: the action picked from the menu, else the next one.
function shownActionOf(chatBar: ChatBarClient, chosenAction: string | null): string {
  return chosenAction && chatBar.actionFidelity ? chosenAction : actionOf(chatBar)
}

// The action button runs what it shows: advance moves the session on, review records the person's approval, and every
// other action is a command the chat runs. Review over violations opens the board on the fidelity, where the person
// reads them and sends Fix. A picked action is run once, and the button then shows the next one again.
async function pressAction($: EngineInterface, chatBar: ChatBarClient, action: string): Promise<void> {
  const fidelity = chatBar.actionFidelity
  await clearChosenAction($)
  if (action === 'advance') return moveNext($, chatBar)
  if (!fidelity) return
  if (action === 'review' && fidelity.violationCount) return openBoard($, fidelity)
  return action === 'review' ? reviewFidelity($, fidelity) : runAction($, fidelity, action)
}

// The orange chip of the canvas, an orange Box holding the next action's icon, then the ▾ that opens
// the picker, its action and fidelity shown above it on hover.
export function ActionButtonView($: EngineInterface, elements: ElementTable, { chatBar, picker }: ChatBarDraw) {
  const { Box, Text } = elements
  const action = shownActionOf(chatBar, picker.chosenAction)
  if (!action) return null
  const target = action === 'advance' ? `move ${chatBar.sessionName} on` : `${action} ${chatBar.actionFidelity?.guidance ?? ''}`
  return (
    <Box key="action" flexDirection="row" gap={0} paddingX={1} backgroundColor={BRAND.accent}>
      {GlyphButtonView(elements, 'next-action', ACTION_ICONS[action] ?? '•', BRAND.onAccent, () => pressAction($, chatBar, action))}
      {GlyphButtonView(elements, 'action-picker', '▾', BRAND.onAccent, () => toggleActionPicker($))}
      <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{target}</Text>
      </Box>
    </Box>
  )
}

// The column the action button starts at on the line: the health mark and its gap, the session name, gap, ▾, gap, │,
// gap, then each dot with its violation count and a gap. The menu opens at it, so it reads as the button's list box.
const NAME_TO_DOTS = 5
const HEALTH_MARK_AND_GAP = 2
function actionColumnOf(chatBar: ChatBarClient): number {
  const dots = chatBar.fidelities.reduce((cells, fidelity) => cells + 1 + (fidelity.violationCount ? String(fidelity.violationCount).length : 0) + 1, 0)
  return HEALTH_MARK_AND_GAP + chatBar.sessionName.length + NAME_TO_DOTS + dots
}

// Every builder action as a menu above the button: its icon, its name, and next beside the fidelity's next one. The one
// on the button is highlighted; picking another puts it on the button in place of the next.
export function PickerView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, picker }: ChatBarDraw) {
  const fidelity = chatBar.actionFidelity
  if (!picker.isOpen || !fidelity) return null
  return (
    <Box key="picker" flexDirection="column" alignSelf="flex-start" marginLeft={actionColumnOf(chatBar)} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {BUILDER_ACTIONS.map(action => {
        const isNext = action === fidelity.nextAction
        const isShown = action === shownActionOf(chatBar, picker.chosenAction)
        return (
          <Box key={`pick-row-${action}`} flexDirection="row" gap={1} alignItems="center" backgroundColor={isShown ? BRAND.accentTint : undefined}>
            <Text color={isShown ? BRAND.accent : BRAND.muted}>{ACTION_ICONS[action]}</Text>
            <Button key={`pick-${action}`} plain label={action} onPress={() => chooseAction($, action)} />
            <Text size="caption" color={BRAND.faint}>{isNext ? 'next' : ''}</Text>
          </Box>
        )
      })}
    </Box>
  )
}
