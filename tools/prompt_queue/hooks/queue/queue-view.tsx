import type { EngineInterface, RenderInput } from 'claude-code'

import {
  clearQueue,
  editPrompt,
  movePrompt,
  removePrompt,
  sendNow,
  queueDraft,
  togglePlaying,
  toggleExpanded,
  toggleSubAgentMode,
  toggleSteps,
  type QueueState,
} from './prompt-queue'
import type { PromptStep, QueuedPrompt } from '../../types'
import { progressOf } from './plan-steps'
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

/** The columns kept at a card's right for its send, edit, move and remove buttons, shown when the pointer is on the card. */
const CARD_BUTTON_COLUMNS = 15
/** The columns around a card's text: the queue box's border and padding, the button's rounded ends, and the gaps. */
const CARD_CHROME_COLUMNS = 10
/** The columns of a button's rounded ends and padding, around its label. */
const BUTTON_END_COLUMNS = 4
/** The columns of the attachment count, a paperclip and a digit or two. */
const ATTACHED_COLUMNS = 4

/** The mark before a step for where it stands: done, being worked, or not started. */
const STEP_MARK = { done: '✓', in_progress: '▸', pending: '○' } as const


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
      paddingX={1} width={state.isExpanded ? '100%' : undefined}>
      {state.isExpanded && QueueListView($, e, state)}
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
 * and remove buttons. A card the agent is working on is drawn bright, one whose steps are all done dim, and a card with
 * steps shows how many are done, which opens them under it.
 */
function QueueListView($: EngineInterface, e: AbovePromptEvent, state: QueueState) {
  const { Box, Text } = $.ui.resolve(e)
  const { queue } = state
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
        <Box key={`card-${prompt.id}`} flexDirection="column">
          {CardView($, e, state, prompt, index)}
          {state.openSteps.includes(prompt.id) && StepsView($, e, prompt.id, prompt.steps ?? [])}
        </Box>
      ))}
    </Box>
  )
}

function CardView($: EngineInterface, e: AbovePromptEvent, state: QueueState, prompt: QueuedPrompt, index: number) {
  const { Box, Text, Button } = $.ui.resolve(e)
  const isEditing = prompt.id === state.editingId
  const isWorking = prompt.id === state.workingId
  const progress = progressOf(prompt.steps)
  const isFinished = progress !== '' && (prompt.steps ?? []).every(step => step.state === 'done')

  return (
    <Box key={`card-row-${prompt.id}`} flexDirection="row" justifyContent="space-between" alignItems="center" gap={1} width="100%">
      {progress !== '' && <Box flexShrink={0}><Button key={`steps-${prompt.id}`} label={progress} onPress={() => toggleSteps($, prompt.id)} /></Box>}
      {(prompt.attachments ?? []).length > 0 && <Box flexShrink={0}><Text key={`attached-${prompt.id}`} color={LOOK.muted}>{`📎${prompt.attachments!.length}`}</Text></Box>}
      <Box flexGrow={1} flexShrink={1}>
        <Button key={`card-text-${prompt.id}`} dimColor={isEditing || isFinished} onPress={() => editPrompt($, prompt)}>
          <Text wrap="truncate-end" color={isEditing ? LOOK.placeholder : isWorking ? LOOK.accent : undefined}
            italic={isEditing} bold={isWorking} dimColor={isFinished}>
            {cutToFit(`${index + 1}. ${prompt.text.replace(/\s+/g, ' ')}${isEditing ? '  (editing)' : ''}`, textColumnsOf(e, prompt, progress))}
          </Text>
        </Button>
      </Box>
      <Box width={CARD_BUTTON_COLUMNS} flexShrink={0} justifyContent="flex-end">
        <Box flexDirection="row" gap={1} display="none" hover={{ display: 'flex' }} backgroundColor={LOOK.keyCap} paddingX="xs">
          <Button key={`send-now-${prompt.id}`} label="↵" onPress={() => sendNow($, prompt)} />
          <Button key={`edit-${prompt.id}`} label="✎" onPress={() => editPrompt($, prompt)} />
          <Button key={`up-${prompt.id}`} label="↑" onPress={() => movePrompt($, index, index - 1)} />
          <Button key={`down-${prompt.id}`} label="↓" onPress={() => movePrompt($, index, index + 1)} />
          <Button key={`remove-${prompt.id}`} label="✕" onPress={() => removePrompt($, prompt.id)} />
        </Box>
      </Box>
    </Box>
  )
}

/** The columns a card's text may take: the chat box's width less the card's rounded ends, the gaps, the hover buttons,
 * and the progress and attachment count drawn before it. A button draws its whole label, so the text is cut here. */
function textColumnsOf(e: AbovePromptEvent, prompt: QueuedPrompt, progress: string): number {
  const progressColumns = progress === '' ? 0 : progress.length + BUTTON_END_COLUMNS + 1
  const attachedColumns = (prompt.attachments ?? []).length === 0 ? 0 : ATTACHED_COLUMNS + 1
  return e.props.bodyColumns - CARD_CHROME_COLUMNS - CARD_BUTTON_COLUMNS - progressColumns - attachedColumns
}

/** Text cut to a width, ending in an ellipsis when it did not fit. */
function cutToFit(text: string, columns: number): string {
  return text.length <= columns ? text : `${text.slice(0, Math.max(0, columns - 1)).trimEnd()}…`
}

/** A card's steps under it, in order: done ones ticked and dim, the one being worked marked and bright. */
function StepsView($: EngineInterface, e: AbovePromptEvent, id: string, steps: PromptStep[]) {
  const { Box, Text } = $.ui.resolve(e)

  return (
    <Box key={`steps-of-${id}`} flexDirection="column" paddingLeft={3}>
      {steps.map((step, index) => (
        <Text key={`step-${id}-${index + 1}`} wrap="truncate-end" dimColor={step.state === 'done'}
          color={step.state === 'in_progress' ? LOOK.accent : undefined}>
          {`${STEP_MARK[step.state]} ${step.text}`}
        </Text>
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
