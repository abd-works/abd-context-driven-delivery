import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { dismissFailure, fixFailure, type FailureClient } from './failure-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// A failure above the chat bar's line: what failed in red, the context it failed in beneath it, Fix to send both to the
// chat, and ✕ to dismiss it. Once Fix is pressed, a running bar stands in its place until the fix is in the chat.
export function FailureView($: EngineInterface, elements: ElementTable, failure: FailureClient | null) {
  const { Box, Button, Progress, Text } = elements
  if (!failure) return null
  return (
    <Box key="failure" flexDirection="column">
      <Box key="failure-line" flexDirection="row" gap={1} alignItems="center">
        <Text color={BRAND.error}>{failure.failure}</Text>
        {failure.isFixing ? (
          <Progress key="fixing-failure" label="Sending the fix to Claude" />
        ) : (
          <Button key="fix-failure" label="Fix" variant="primary" onPress={() => fixFailure($, failure)} />
        )}
        {GlyphButtonView(elements, 'dismiss-failure', '✕', BRAND.muted, () => dismissFailure($, failure))}
      </Box>
      <Text key="failure-context" color={BRAND.muted}>{failure.context}</Text>
    </Box>
  )
}
