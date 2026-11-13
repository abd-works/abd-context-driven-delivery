import type { EngineInterface } from 'claude-code'

import type { FidelityHelpJson } from '../../types'
import { BRAND } from '../shared/brand'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The help pane: the fidelity's help drawn as markdown, which the pane scrolls.
export function FidelityHelpView(elements: ElementTable, help: FidelityHelpJson) {
  const { Box, Markdown, Text } = elements
  if (!help) return <Text color={BRAND.muted}>No help open.</Text>
  return (
    <Box key="help" flexDirection="column" paddingX={1}>
      <Markdown key="help-markdown" text={help.markdown} />
    </Box>
  )
}
