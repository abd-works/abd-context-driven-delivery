import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { chooseAction, clearChosenAction, toggleActionPicker } from './action-picker-client'
import { moveNext, type ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { runActionOn } from './fidelity-progress-client'
import { formatArgumentOf, resetFormats, type FormatChips } from './format-choices-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The canvas's glyph for each action a stage sends and for advance, the button's own move to the next stage: play,
// check, eye, cycle, pencil, open-out, page, and the move-on arrow. An action the canvas has no glyph for shows a dot.
const ACTION_ICONS: Record<string, string> = { generate: '▶', validate: '✓', iterate: '↻', sketch: '✎', render: '↗', document: '▯', advance: '➜' }
const iconOf = (action: string): string => ACTION_ICONS[action] ?? '•'

// The action the button shows: advance once the stage is done, else the action fidelity's next action, else, for a
// fidelity with nothing next, such as one already done, the stage's first action, so ▶ and its ▾ list stay on the band.
export function actionOf(chatBar: ChatBarClient): string {
  if (chatBar.canMoveNext) return 'advance'
  const fidelity = chatBar.actionFidelity
  if (!fidelity) return ''
  return fidelity.nextAction || (chatBar.actions[0] ?? '')
}

// What the button shows and runs: the action picked from the menu, else the next one.
export function shownActionOf(chatBar: ChatBarClient, chosenAction: string | null): string {
  return chosenAction && chatBar.actionFidelity ? chosenAction : actionOf(chatBar)
}

// The action button runs what it shows: advance moves the session on, and every other action is a command the chat runs. A picked action is run once, and the button then shows the next one again.
async function pressAction($: EngineInterface, chatBar: ChatBarClient, formats: FormatChips, action: string): Promise<unknown> {
  const fidelity = chatBar.actionFidelity
  await clearChosenAction($)
  if (action === 'advance') return moveNext($, chatBar)
  if (!fidelity) return
  const formatArgument = formatArgumentOf(chatBar, formats, action)
  await runActionOn($, chatBar.actionFidelities, action, formatArgument)
  if (formatArgument) await resetFormats($)
}

// The orange chip of the canvas, an orange Box holding the next action's icon, then the ▾ that opens
// the picker, its action and fidelity shown above it on hover.
export function ActionButtonView($: EngineInterface, elements: ElementTable, { chatBar, picker, formats }: ChatBarDraw) {
  const { Box, Text } = elements
  const action = shownActionOf(chatBar, picker.chosenAction)
  if (!action) return null
  const target = action === 'advance' ? `move ${chatBar.sessionName} on` : `${action} ${chatBar.actionFidelities.map(fidelity => fidelity.slug).join(' ')}`
  return (
    <Box key="action" flexDirection="row" gap={0} paddingX={1} backgroundColor={BRAND.accent}>
      {GlyphButtonView(elements, 'next-action', iconOf(action), BRAND.onAccent, () => pressAction($, chatBar, formats, action))}
      {GlyphButtonView(elements, 'action-picker', '▾', BRAND.onAccent, () => toggleActionPicker($))}
      <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{target}</Text>
      </Box>
    </Box>
  )
}

// The column the action button starts at on the line: the health mark and its gap, the stage chip and its gap, │ and
// its gap, then each dot with its violation count and a gap. The menu opens at it, so it reads as the button's list box.
const HEALTH_STAGE_AND_SEPARATOR = 9
export function actionColumnOf(chatBar: ChatBarClient): number {
  const dots = chatBar.fidelities.reduce((cells, fidelity) => cells + 1 + (fidelity.violationCount ? String(fidelity.violationCount).length : 0) + 1, 0)
  return HEALTH_STAGE_AND_SEPARATOR + dots
}

// Every action the shown stage sends, as a menu above the button: its icon, its name, and next beside the fidelity's
// next one. The one on the button is highlighted; picking another puts it on the button in place of the next.
export function PickerView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, picker }: ChatBarDraw) {
  const fidelity = chatBar.actionFidelity
  if (!picker.isOpen || !fidelity) return null
  return (
    <Box key="picker" flexDirection="column" alignSelf="flex-start" marginLeft={actionColumnOf(chatBar)} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {chatBar.actions.map(action => {
        const isNext = action === fidelity.nextAction
        const isShown = action === shownActionOf(chatBar, picker.chosenAction)
        return (
          <Box key={`pick-row-${action}`} flexDirection="row" gap={1} alignItems="center" backgroundColor={isShown ? BRAND.accentTint : undefined}>
            <Text color={isShown ? BRAND.accent : BRAND.muted}>{iconOf(action)}</Text>
            <Button key={`pick-${action}`} plain label={action} onPress={() => chooseAction($, action)} />
            <Text size="caption" color={BRAND.faint}>{isNext ? 'next' : ''}</Text>
          </Box>
        )
      })}
    </Box>
  )
}
