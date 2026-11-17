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
  toggleOpenedCard,
  robotPromptsOf,
  agentNameOf,
  renameAgent,
  addStep,
  moveStep,
  removeStep,
  type QueueState,
} from './prompt-queue'
import type { PromptStep, QueuedPrompt, SubAgentTask } from '../../types'
import { progressOf } from './plan-steps'
import {
  ADD_SVG,
  CLEAR_SVG,
  IconButtonView,
  LOOK,
  PAUSE_SVG,
  PLAY_SVG,
  stackSvgOf,
  SUB_AGENTS_SVG,
  type Icon,
  robotSvgOf,
} from './icon-button-view'

type AbovePromptEvent = RenderInput<'AbovePrompt'>

/**
 * The columns kept for + while it is hidden, so revealing it changes no size and the stack image stays where it is:
 * a revealed Box that resized the row made the stack image vanish on the desktop.
 */
const ADD_COLUMNS = 3

/** The columns kept at a card's right for its send, edit, move and remove buttons, shown when the pointer is on the card. */
const CARD_BUTTON_COLUMNS = 15

/** The columns kept before a card's text for its task button, 3/3 or +, so every card's text starts in one place. */
const TASK_BUTTON_COLUMNS = 6

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
      {state.isExpanded && (state.isSubAgentMode && state.tasks.length > 0 ? AgentColumnsView($, e, state) : QueueListView($, e, state))}
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
  if (state.queue.isEmpty) {
    return null
  }

  return CardsView($, e, state, state.queue.prompts)
}

/** A stack of the queue's cards, each with its steps open under it when they are opened. A card keeps its place in the
 * whole queue, so its ↑ and ↓ move it there. */
function CardsView($: EngineInterface, e: AbovePromptEvent, state: QueueState, prompts: QueuedPrompt[], isInColumn = false) {
  const { Box } = $.ui.resolve(e)
  const all = state.queue.prompts

  return (
    <Box flexDirection="column" rowGap="sm" width="100%">
      {prompts.map(prompt => (
        <Box key={`card-${prompt.id}`} flexDirection="column">
          {CardView($, e, state, prompt, all.indexOf(prompt), isInColumn)}
          {state.openSteps.includes(prompt.id) && (prompt.steps ?? []).length > 0 && StepsView($, e, prompt)}
        </Box>
      ))}
    </Box>
  )
}

/** One card. In a robot's narrow queue it shows no buttons of its own; pressing it opens it in place, its buttons on a
 * row beneath it, and pressing it again closes it. */
function CardView($: EngineInterface, e: AbovePromptEvent, state: QueueState, prompt: QueuedPrompt, index: number, isInColumn = false) {
  const { Box, Text, Button } = $.ui.resolve(e)
  const isEditing = prompt.id === state.editingId
  const isWorking = prompt.id === state.workingId
  const progress = progressOf(prompt.steps)
  const isFinished = Boolean(prompt.is_done)

  const isOpened = isInColumn && prompt.id === state.openedId
  const row = (
    <Box key={`card-row-${prompt.id}`} flexDirection="row" justifyContent="space-between" alignItems="center" gap={1} width="100%">
      <Box width={TASK_BUTTON_COLUMNS} flexShrink={0}>
        {progress !== ''
          ? <Button key={`steps-${prompt.id}`} label={progress} onPress={() => toggleSteps($, prompt.id)} />
          : !isFinished && <Button key={`steps-${prompt.id}`} label="+" onPress={() => addStep($, prompt)} />}
      </Box>
      {(prompt.attachments ?? []).length > 0 && <Text key={`attached-${prompt.id}`} color={LOOK.muted}>{`📎${prompt.attachments!.length}`}</Text>}
      <Box flexGrow={1} flexShrink={1} minWidth={0}
        borderStyle={isWorking ? 'round' : undefined} borderColor={isWorking ? LOOK.accent : undefined}>
        <Button key={`card-text-${prompt.id}`} dimColor={isEditing || isFinished} onPress={() => (isInColumn ? toggleOpenedCard($, prompt.id) : editPrompt($, prompt))}>
          <Text wrap="wrap" color={isEditing ? LOOK.placeholder : isWorking ? LOOK.accent : undefined}
            italic={isEditing} bold={isWorking} underline={isWorking} dimColor={isFinished}>
            {`${index + 1}. ${prompt.text.replace(/\s+/g, ' ')}${isEditing ? '  (editing)' : ''}`}
          </Text>
        </Button>
      </Box>
      {!isInColumn && <Box width={CARD_BUTTON_COLUMNS} justifyContent="flex-end">
        <Box flexDirection="row" gap={1} display="none" hover={{ display: 'flex' }} backgroundColor={LOOK.keyCap} paddingX="xs">
          {CardButtonsView($, e, prompt, index)}
        </Box>
      </Box>}
    </Box>
  )
  if (!isOpened) {
    return row
  }

  return (
    <Box key={`card-opened-${prompt.id}`} flexDirection="column" width="100%">
      {row}
      <Box flexDirection="row" gap={1} paddingLeft={TASK_BUTTON_COLUMNS + 1}>{CardButtonsView($, e, prompt, index)}</Box>
    </Box>
  )
}

/** A card's own buttons: send now, edit, move up and down, and remove. */
function CardButtonsView($: EngineInterface, e: AbovePromptEvent, prompt: QueuedPrompt, index: number) {
  const { Button } = $.ui.resolve(e)

  return [
    <Button key={`send-now-${prompt.id}`} label="↵" onPress={() => sendNow($, prompt)} />,
    <Button key={`edit-${prompt.id}`} label="✎" onPress={() => editPrompt($, prompt)} />,
    <Button key={`up-${prompt.id}`} label="↑" onPress={() => movePrompt($, index, index - 1)} />,
    <Button key={`down-${prompt.id}`} label="↓" onPress={() => movePrompt($, index, index + 1)} />,
    <Button key={`remove-${prompt.id}`} label="✕" onPress={() => removePrompt($, prompt.id)} />,
  ]
}

/** Sub-agent mode: one queue for each sub-agent, side by side, in the place of the queue's list, each the same cards. */
function AgentColumnsView($: EngineInterface, e: AbovePromptEvent, state: QueueState) {
  const { Box } = $.ui.resolve(e)

  return (
    <Box key="agent-columns" flexDirection="row" gap={1} width="100%">
      {state.tasks.map((task, place) => AgentColumnView($, e, state, task, place))}
    </Box>
  )
}

/** One sub-agent's queue: its robot on top with its name and ✎ to rename it, then its prompts as the queue's cards. */
function AgentColumnView($: EngineInterface, e: AbovePromptEvent, state: QueueState, task: SubAgentTask, place: number) {
  const elements = $.ui.resolve(e)
  const { Box, Button, Text } = elements
  const number = place + 1
  const name = agentNameOf(task, place)
  const robot = 'Svg' in elements
    ? <elements.Svg key={`robot-${number}`} source={robotSvgOf(place)} alt={`${name}, a robot`} width={ROBOT_PIXELS} height={ROBOT_PIXELS} />
    : <Text key={`robot-${number}`} color={LOOK.accent}>🤖</Text>

  return (
    <Box key={`agent-column-${number}`} flexDirection="column" flexGrow={1} minWidth={0} rowGap="sm">
      <Box flexDirection="row" alignItems="center" gap={1}>
        {robot}
        <Text bold color={LOOK.accent}>{name}</Text>
        <Button key={`rename-agent-${number}`} label="✎" onPress={() => renameAgent($, place)} />
      </Box>
      {CardsView($, e, state, robotPromptsOf(state.queue.prompts, task, place), true)}
    </Box>
  )
}

/** About two lines tall, in the desktop's pixels: a robot stands out over its column. */
const ROBOT_PIXELS = 28

/** A card's steps under it, in order: done ones ticked and dim, the one being worked marked and bright. */
function StepsView($: EngineInterface, e: AbovePromptEvent, prompt: QueuedPrompt) {
  const { Box, Button } = $.ui.resolve(e)

  return (
    <Box key={`steps-of-${prompt.id}`} flexDirection="column" paddingLeft={TASK_BUTTON_COLUMNS + 1}>
      {(prompt.steps ?? []).map((step, index) => StepView($, e, prompt, step, index))}
      <Box flexDirection="row">
        <Button key={`add-step-${prompt.id}`} label="+" onPress={() => addStep($, prompt)} />
      </Box>
    </Box>
  )
}

/** One task under its card: its mark and text, and, with the pointer on it, ↑ ↓ to move it and ✕ to take it off. */
function StepView($: EngineInterface, e: AbovePromptEvent, prompt: QueuedPrompt, step: PromptStep, index: number) {
  const { Box, Button, Text } = $.ui.resolve(e)
  const number = index + 1

  return (
    <Box key={`step-row-${prompt.id}-${number}`} flexDirection="row" justifyContent="space-between" gap={1}>
      <Box flexGrow={1} flexShrink={1} minWidth={0}>
        <Text key={`step-${prompt.id}-${number}`} wrap="wrap" dimColor={step.state === 'done'}
          color={step.state === 'in_progress' ? LOOK.accent : undefined}>
          {`${STEP_MARK[step.state]} ${step.text}`}
        </Text>
      </Box>
      <Box flexDirection="row" gap={1} display="none" hover={{ display: 'flex' }} backgroundColor={LOOK.keyCap} paddingX="xs">
        <Button key={`up-step-${prompt.id}-${number}`} label="↑" onPress={() => moveStep($, prompt, index, index - 1)} />
        <Button key={`down-step-${prompt.id}-${number}`} label="↓" onPress={() => moveStep($, prompt, index, index + 1)} />
        <Button key={`remove-step-${prompt.id}-${number}`} label="✕" onPress={() => removeStep($, prompt, index)} />
      </Box>
    </Box>
  )
}
