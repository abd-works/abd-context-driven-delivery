import type { EngineInterface, RenderInput } from 'claude-code'

import {
  clearQueue,
  editPrompt,
  movePrompt,
  removePrompt,
  queueDraft,
  togglePlaying,
  toggleExpanded,
  toggleSubAgentMode,
  type QueueState,
} from './prompt-queue'
import type { PromptQueue } from './queue-order'
import {
  ADD_SVG,
  CLEAR_SVG,
  IconButtonView,
  LOOK,
  PAUSE_SVG,
  PLAY_SVG,
  stackSvgOf,
  ALT_KEY,
  ENTER_KEY,
  KEY_CAP_PIXELS,
  keyCapSvgOf,
  keyCapWidthOf,
  SUB_AGENTS_SVG,
  type Icon,
  type KeyCap,
} from './icon-button-view'

type AbovePromptEvent = RenderInput<'AbovePrompt'>

/**
 * The columns kept for + while it is hidden, so revealing it changes no size and the stack image stays where it is:
 * a revealed Box that resized the row made the stack image vanish on the desktop.
 */
const ADD_COLUMNS = 3

/** The columns kept at a card's right for its edit, move and remove buttons, shown when the pointer is on the card. */
const CARD_BUTTON_COLUMNS = 12

/**
 * Its own box above the chat bar. At rest it shows only the stack image, the count drawn on it, and the pointer over
 * the box reveals + beside it; the stack image opens the queue as a stack of task cards with the other controls. The
 * controls sit at the bottom, next to the chat bar, and the cards open above them, so no button moves as it opens.
 */
export function QueueView($: EngineInterface, e: AbovePromptEvent, state: QueueState) {
  const elements = $.ui.resolve(e)
  const { Box, Text } = elements
  const { queue } = state

  return (
    <Box key="prompt-queue" flexDirection="column" rowGap="sm" alignSelf="flex-start"
      paddingX={1} width={state.isExpanded ? e.props.bodyColumns : undefined}>
      {state.isExpanded && QueueListView($, e, queue, state.editingId)}
      {state.isExpanded && state.isSubAgentMode && state.tasks.map(task => (
        <Text dimColor wrap="truncate-end">{`  ↳ ${task.description}: ${task.prompts.length} prompt(s)`}</Text>
      ))}
      {state.notice !== '' && <Text color="warning">{state.notice}</Text>}
      <Box flexDirection="row" gap={1}>
        {IconButtonView(elements, stackIcon(state), () => toggleExpanded($))}
        <Box width={ADD_COLUMNS}>
          {state.isExpanded
            ? IconButtonView(elements, ADD_ICON, () => queueDraft($))
            : <Box display="none" hover={{ display: 'flex' }}>{IconButtonView(elements, ADD_ICON, () => queueDraft($))}</Box>}
        </Box>
        {state.isExpanded && IconButtonView(elements, playIcon(state), () => togglePlaying($))}
        {state.isExpanded && IconButtonView(elements, subAgentsIcon(state), () => toggleSubAgentMode($))}
        {state.isExpanded && IconButtonView(elements, CLEAR_ICON, () => clearQueue($))}
      </Box>
    </Box>
  )
}

function stackIcon(state: QueueState): Icon {
  const tip = state.isExpanded ? 'Collapse the prompt queue' : `${state.queue.size} queued: open the prompt queue`
  return { key: 'queue-stack', svg: stackSvgOf(state.queue.size), glyph: `≡${state.queue.size}`, tip, isOn: state.isExpanded }
}

/** Play while paused, pause while playing: the icon shows what a press does next. */
function playIcon(state: QueueState): Icon {
  return state.isPlaying
    ? { key: 'queue-play', svg: PAUSE_SVG, glyph: '‖', tip: 'Pause: finished turns no longer send the next prompt', isOn: true }
    : { key: 'queue-play', svg: PLAY_SVG, glyph: '▶', tip: 'Play: send the next prompt now and after every finished turn' }
}

function subAgentsIcon(state: QueueState): Icon {
  const tip = state.isSubAgentMode
    ? 'Sub-agent mode on: a finished turn sends each grouped task to its own sub-agent'
    : 'Sub-agent mode off: a finished turn sends the next prompt'
  return { key: 'queue-sub-agents', svg: SUB_AGENTS_SVG, glyph: '⑂', tip, isOn: state.isSubAgentMode }
}

const ADD_ICON: Icon = { key: 'queue-add', svg: ADD_SVG, glyph: '+', tip: 'Queue the draft (Alt+Enter)' }
const CLEAR_ICON: Icon = { key: 'queue-clear', svg: CLEAR_SVG, glyph: '✕', tip: 'Clear the queue' }

/**
 * The open queue, one line per task, each drawn as the chat's own rounded buttons are, the session name's among them,
 * so a card is one line tall with round ends. Pressing a card edits it; the pointer over it reveals its edit, move
 * and remove buttons at its right. The text shrinks and truncates, so a long prompt never pushes them past the
 * chat's edge.
 */
function QueueListView($: EngineInterface, e: AbovePromptEvent, queue: PromptQueue, editingId: string) {
  const { Box, Text, Button } = $.ui.resolve(e)
  if (queue.isEmpty) {
    return (
      <Box flexDirection="row" justifyContent="flex-end" alignItems="center" gap={2} borderStyle="round"
        borderColor={LOOK.card} backgroundColor={LOOK.card} paddingX="xs">
        <Box flexDirection="row" alignItems="center" gap="xs">
          <Text color={LOOK.placeholder}>Add</Text>
          {KeyCapView($, e, ALT_KEY)}
          {KeyCapView($, e, ENTER_KEY)}
        </Box>
      </Box>
    )
  }

  return (
    <Box flexDirection="column" rowGap="sm">
      {queue.prompts.map((prompt, index) => (
        <Box key={`card-${prompt.id}`} flexDirection="row" justifyContent="space-between" alignItems="center" gap={1}>
          <Box flexGrow={1} flexShrink={1} minWidth={0}>
            <Button key={`card-text-${prompt.id}`} onPress={() => editPrompt($, prompt)}>
              <Text wrap="truncate-end" color={prompt.id === editingId ? LOOK.placeholder : undefined} italic={prompt.id === editingId}>
                {`${index + 1}. ${prompt.text.replace(/\s+/g, ' ')}${prompt.id === editingId ? '  (editing)' : ''}`}
              </Text>
            </Button>
          </Box>
          <Box width={CARD_BUTTON_COLUMNS} flexShrink={0} justifyContent="flex-end">
            <Box flexDirection="row" gap={1} display="none" hover={{ display: 'flex' }}>
              <Button key={`edit-${prompt.id}`} label="✎" onPress={() => editPrompt($, prompt)} />
              <Button key={`up-${prompt.id}`} label="↑" onPress={() => movePrompt($, index, index - 1)} />
              <Button key={`down-${prompt.id}`} label="↓" onPress={() => movePrompt($, index, index + 1)} />
              <Button key={`remove-${prompt.id}`} label="✕" onPress={() => removePrompt($, prompt.id)} />
            </Box>
          </Box>
        </Box>
      ))}
    </Box>
  )
}

/** A key the person presses, drawn as the chat's image buttons are; a surface with no Svg shows its glyph on grey. */
function KeyCapView($: EngineInterface, e: AbovePromptEvent, key: KeyCap) {
  const elements = $.ui.resolve(e)
  if ('Svg' in elements) {
    return <elements.Svg source={keyCapSvgOf(key)} alt={key.glyph} width={keyCapWidthOf(key)} height={KEY_CAP_PIXELS} />
  }
  const { Box, Text } = elements

  return (
    <Box backgroundColor={LOOK.keyCap} paddingX={1}>
      <Text color={LOOK.keyText}>{key.glyph}</Text>
    </Box>
  )
}
