import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import type { ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { openFiles } from './fidelity-files-client'
import { selectFidelity, type FidelityProgressClient } from './fidelity-progress-client'
import { closeCard } from './session-dialogs-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The hover group of the session name and its card: the pointer on either keeps the card shown.
export const CARD_SCOPE = 'session-card'

// The card's columns. name starts the fidelities where the dots start on the line: the session name, gap, ▾, gap, │,
// gap, inside the card's border and padding, which take the two cells the health mark and its gap take on the line.
// fidelities fits the widest fidelity row, so every folder starts in one column.
type CardColumns = { name: number; fidelities: number }
const NAME_TO_DOTS = 5
const FOLDER_GAP = 3

function rowWidthOf(fidelity: FidelityProgressClient): number {
  return `■ ${fidelity.name} ${fidelity.mark} ${fidelity.word}`.length
}

function cardColumnsOf(chatBar: ChatBarClient): CardColumns {
  return { name: chatBar.sessionName.length + NAME_TO_DOTS, fidelities: Math.max(0, ...chatBar.fidelities.map(rowWidthOf)) + FOLDER_GAP }
}

// The session name, then the shown stage in orange, on one line that never wraps, and a ✕ at the far end, apart from the
// stage, that closes a card pinned open.
function HeaderView($: EngineInterface, elements: ElementTable, chatBar: ChatBarClient, _columns: CardColumns) {
  const { Box, Text } = elements
  return (
    <Box key="card-header" flexDirection="row" gap={2} alignItems="center">
      <Text weight="bold" color={BRAND.text} wrap="truncate-end">{chatBar.sessionName}</Text>
      <Text weight="bold" color={BRAND.accent}>{chatBar.shownStage}</Text>
      <Box flexGrow={1} />
      {GlyphButtonView(elements, 'card-close', '✕', BRAND.muted, () => closeCard($))}
    </Box>
  )
}

// One fidelity under the dots: its square, its name and its state, underlined when selected, the whole line one press
// that selects it; its folder beside it as a small chip, a press showing its files, on the first line of that folder.
function FidelityRowView($: EngineInterface, elements: ElementTable, fidelity: FidelityProgressClient, columns: CardColumns, isFolderShown: boolean) {
  const { Box, Button, Text } = elements
  const nameColour = fidelity.state === 'not_started' ? BRAND.muted : BRAND.text
  return (
    <Box key={`card-${fidelity.slug}`} flexDirection="row" marginLeft={columns.name} alignItems="center">
      <Box width={columns.fidelities}>
        <Box key={`card-cell-${fidelity.slug}`} flexDirection="row" gap={1} alignItems="center">
          <Text color={fidelity.shade}>■</Text>
          <Text color={nameColour} underline={fidelity.isSelected}>{fidelity.name}</Text>
          <Text color={fidelity.lookColour} underline={fidelity.isSelected}>{`${fidelity.mark} ${fidelity.word}`}</Text>
          <Box position="absolute" top={0} left={0} width={rowWidthOf(fidelity)}>
            <Button key={`card-pick-${fidelity.slug}`} plain label=" " onPress={() => selectFidelity($, fidelity)} />
          </Box>
        </Box>
      </Box>
      {isFolderShown ? (
        <Box key={`card-folder-chip-${fidelity.slug}`} paddingX={1} backgroundColor={BRAND.surface}>
          {GlyphButtonView(elements, `card-folder-${fidelity.slug}`, `▸ ${fidelity.folder}`, BRAND.muted, () => openFiles($, fidelity))}
        </Box>
      ) : null}
    </Box>
  )
}

// The session card above the line: the server health panel on top, then, once there is a session, the canvas's
// orange-edged card of the shown stage's fidelities. Hovering the session name or the health mark shows it; a press on
// either pins it, and ✕ or another press closes it.
export function SessionCardView($: EngineInterface, elements: ElementTable, { chatBar, view, health }: ChatBarDraw) {
  const { Box } = elements
  const shown = view.isCardOpen ? {} : { display: 'none' as const, hover: { display: 'flex' as const, scope: CARD_SCOPE } }
  const columns = cardColumnsOf(chatBar)
  return (
    <Box key="session-card" flexDirection="column">
      <Box flexDirection="column" gap={1} {...shown}>
        {health.panel}
        {chatBar.hasSession ? (
          <Box key="card-grid" flexDirection="column" paddingX={1} borderStyle="round" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
            {HeaderView($, elements, chatBar, columns)}
            {chatBar.fidelities.map(fidelity => FidelityRowView($, elements, fidelity, columns, chatBar.foldersListedBeside.has(fidelity.slug)))}
          </Box>
        ) : null}
      </Box>
    </Box>
  )
}
