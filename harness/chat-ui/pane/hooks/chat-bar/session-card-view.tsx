import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import type { ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { openFiles, openReport } from './fidelity-files-client'
import { selectFidelity, type FidelityProgressClient } from './fidelity-progress-client'
import { closeCard } from './session-dialogs-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The hover group of the session name and its card: the pointer on either keeps the card shown.
export const CARD_SCOPE = 'session-card'

// The width of the fidelity column, fitting the widest row, so every folder chip starts in one column.
type CardColumns = { fidelities: number }
const FOLDER_GAP = 3

function rowWidthOf(fidelity: FidelityProgressClient): number {
  return `■ ${fidelity.name} ${fidelity.mark} ${fidelity.word}`.length
}

function cardColumnsOf(chatBar: ChatBarClient): CardColumns {
  return { fidelities: Math.max(0, ...chatBar.fidelities.map(rowWidthOf)) + FOLDER_GAP }
}

// The shown stage in orange over the fidelities, and at the right end the session name and a ✕ that closes a card
// pinned open.
function HeaderView($: EngineInterface, elements: ElementTable, chatBar: ChatBarClient) {
  const { Box, Text } = elements
  return (
    <Box key="card-header" flexDirection="row" gap={2} alignItems="center">
      <Text weight="bold" color={BRAND.accent}>{chatBar.shownStage}</Text>
      <Box flexGrow={1} />
      <Text weight="bold" color={BRAND.text} wrap="truncate-end">{chatBar.sessionName}</Text>
      {GlyphButtonView(elements, 'card-close', '✕', BRAND.muted, () => closeCard($))}
    </Box>
  )
}

// One fidelity under the dots: its square and its name, underlined when selected, one press that selects it as a press on
// its dot does; its state beside them, a press on violations opening the validation report as the count on the line does;
// its folder beside it as a small chip, a press showing its files, on the first line of that folder.
function FidelityRowView($: EngineInterface, elements: ElementTable, fidelity: FidelityProgressClient, columns: CardColumns, isFolderShown: boolean) {
  const { Box, Button, Text } = elements
  const nameColour = fidelity.state === 'not_started' ? BRAND.muted : BRAND.text
  const state = <Text key={`card-state-words-${fidelity.slug}`} color={fidelity.lookColour} underline={fidelity.isSelected}>{`${fidelity.mark} ${fidelity.word}`}</Text>
  return (
    <Box key={`card-${fidelity.slug}`} flexDirection="row" alignItems="center">
      <Box width={columns.fidelities}>
        <Box key={`card-cell-${fidelity.slug}`} flexDirection="row" gap={1} alignItems="center">
          <Button key={`card-pick-${fidelity.slug}`} plain onPress={() => selectFidelity($, fidelity)}>
            <Text key="card-square" color={fidelity.shade}>{'■ '}</Text>
            <Text key="card-name" color={nameColour} underline={fidelity.isSelected}>{fidelity.name}</Text>
          </Button>
          {fidelity.violationCount ? (
            <Button key={`card-report-${fidelity.slug}`} plain onPress={() => openReport($, fidelity)}>{state}</Button>
          ) : state}
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

// The session card above the line, as wide as the chat with a line of space below it: the server health panel on top,
// then, once there is a session, the shown stage's fidelities directly under it. Hovering the session name or the
// health mark shows it; a press on either pins it, and ✕ or another press closes it.
export function SessionCardView($: EngineInterface, elements: ElementTable, { chatBar, view, health }: ChatBarDraw) {
  const { Box } = elements
  const shown = view.isCardOpen ? {} : { display: 'none' as const, hover: { display: 'flex' as const, scope: CARD_SCOPE } }
  const columns = cardColumnsOf(chatBar)
  return (
    <Box key="session-card" flexDirection="column">
      <Box flexDirection="column" marginBottom={1} {...shown}>
        {health.panel}
        {chatBar.hasSession ? (
          <Box key="card-grid" flexDirection="column" paddingX={1} paddingY={1} borderStyle="round" borderColor={BRAND.card} backgroundColor={BRAND.card}>
            {HeaderView($, elements, chatBar)}
            {chatBar.fidelities.map(fidelity => FidelityRowView($, elements, fidelity, columns, chatBar.foldersListedBeside.has(fidelity.slug)))}
          </Box>
        ) : null}
      </Box>
    </Box>
  )
}
