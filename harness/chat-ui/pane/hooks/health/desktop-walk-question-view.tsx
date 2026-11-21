import type { EngineInterface } from 'claude-code'

import type { DesktopWalkQuestionJson } from '../../types'
import { BRAND } from '../shared/brand'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

export type DesktopWalkActions = { answer: (isYes: boolean) => unknown }

// Asked before a timed e2e run's desktop walk: the walk takes the person's screen and keyboard, so it runs only on
// their yes. Not now, or no answer within ten minutes, leaves the e2e run to go on without the walk.
export function DesktopWalkQuestionView(elements: ElementTable, question: DesktopWalkQuestionJson | null, actions: DesktopWalkActions) {
  const { Box, Button, Text } = elements
  if (!question) return null
  return (
    <Box key="desktop-walk-question" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>Run the desktop walk now?</Text>
      <Text color={BRAND.muted}>{question.message}</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="desktop-walk-no" label="Not now" onPress={() => actions.answer(false)} />
        <Button key="desktop-walk-yes" label="Run the walk" variant="primary" onPress={() => actions.answer(true)} />
      </Box>
    </Box>
  )
}
