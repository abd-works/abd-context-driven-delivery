import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { GlyphButtonView } from '../glyph-button-view'
import type { ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { selectFidelity, type FidelityClient } from './fidelity-client'
import { openFiles } from './fidelity-files-client'
import { closeCard } from './session-dialogs-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The hover group of the session name and its card: the pointer on either keeps the card shown.
export const CARD_SCOPE = 'session-card'

// The session name, the shown stage in orange, and a ✕ that closes a card pinned open.
function HeaderView($: EngineInterface, elements: ElementTable, chatBar: ChatBarClient) {
  const { Box, Text } = elements
  return (
    <Box key="card-header" flexDirection="row" gap={2}>
      <Text weight="bold" color={BRAND.text}>{chatBar.sessionName}</Text>
      <Box key="card-stage">
        <Text weight="bold" color={BRAND.accent}>{chatBar.shownStage}</Text>
      </Box>
      <Box flexGrow={1} />
      {GlyphButtonView(elements, 'card-close', '✕', BRAND.muted, () => closeCard($))}
    </Box>
  )
}

// One fidelity on one row: its square, its name (a press selects it), its state, and its folder (a press shows its
// files). The row flows instead of keeping columns, since the desktop draws in a proportional font.
function FidelityRowView($: EngineInterface, elements: ElementTable, fidelity: FidelityClient) {
  const { Box, Text } = elements
  const nameColour = fidelity.status === 'not_started' ? BRAND.muted : BRAND.text
  return (
    <Box key={`card-${fidelity.fidelity}`} flexDirection="row" gap={2} alignItems="center">
      <Box key={`card-cell-${fidelity.fidelity}`} flexDirection="row" gap={1} alignItems="center">
        <Text color={fidelity.shade}>■</Text>
        {GlyphButtonView(elements, `card-pick-${fidelity.fidelity}`, fidelity.name, nameColour, () => selectFidelity($, fidelity), fidelity.isSelected)}
        <Text color={fidelity.lookColour} wrap="truncate">{`${fidelity.mark} ${fidelity.word}`}</Text>
      </Box>
      {fidelity.folder ? GlyphButtonView(elements, `card-folder-${fidelity.fidelity}`, `▸ ${fidelity.folder}`, BRAND.faint, () => openFiles($, fidelity)) : null}
    </Box>
  )
}

// The session card above the line: the server health panel on top, then, once there is a session, the canvas's
// orange-edged card of the shown stage's fidelities. Hovering the session name or the health mark shows it; a press on
// either pins it, and ✕ or another press closes it.
export function SessionCardView($: EngineInterface, elements: ElementTable, { chatBar, view, health }: ChatBarDraw) {
  const { Box } = elements
  const shown = view.isCardOpen ? {} : { display: 'none' as const, hover: { display: 'flex' as const, scope: CARD_SCOPE } }
  return (
    <Box key="session-card" flexDirection="column">
      <Box flexDirection="column" gap={1} alignSelf="flex-start" {...shown}>
        {health.panel}
        {chatBar.hasSession ? (
          <Box key="card-grid" flexDirection="column" paddingX={1} borderStyle="round" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
            {HeaderView($, elements, chatBar)}
            {chatBar.fidelities.map(fidelity => FidelityRowView($, elements, fidelity))}
          </Box>
        ) : null}
      </Box>
    </Box>
  )
}
