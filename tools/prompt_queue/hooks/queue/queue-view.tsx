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
  toggleAgentQueue,
  robotPromptsOf,
  agentNameOf,
  renameAgent,
  addStep,
  moveStep,
  removeStep,
  pointerOf,
  sendStepNow,
  editStep,
  movePointerUp,
  movePointerDown,
  stepPointerOf,
  moveStepPointerUp,
  moveStepPointerDown,
  type QueueState,
} from './prompt-queue'
import type { PromptStep, QueuedPrompt, SubAgentTask } from '../../types'
import { progressOf } from './plan-steps'
import {
  ADD_SVG,
  CLEAR_SVG,
  IconButtonView,
  TipView,
  TipLabelView,
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

/** The columns kept before a card's text for its task button, 3/3 or +, so every card's text starts in one place. */
const TASK_BUTTON_COLUMNS = 6

/** The columns every step keeps before its text for the step pointer's ▲ and ▼, empty where the pointer is not, so no
 * step's text moves when the pointer does. */
const POINTER_COLUMNS = 11

/** A space the desktop never collapses: a label of ordinary spaces shrinks to nothing, so its button takes no press. */
const NO_BREAK_SPACE = ' '

/** The invisible button's label over a card: blank and wider than any card, so its press area covers the whole card. */
const CARD_PRESS_AREA = NO_BREAK_SPACE.repeat(200)

/** The invisible button's label over a task box: blank and as wide as the box. */
const TASK_PRESS_AREA = NO_BREAK_SPACE.repeat(TASK_BUTTON_COLUMNS)

/** The columns the card's ↵ ✎ ↑ ↓ ✕ bar takes: it floats over the card's right end, this far left of its right edge. */
const CARD_BAR_COLUMNS = 23

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

const ADD_ICON: Icon = { key: 'queue-add', svg: ADD_SVG, glyph: '+', tip: 'Run /queue on the draft: place it into the plan (Alt+Enter queues it as it is)' }
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
function CardsView($: EngineInterface, e: AbovePromptEvent, state: QueueState, prompts: QueuedPrompt[]) {
  const { Box } = $.ui.resolve(e)
  const all = state.queue.prompts
  const pointer = pointerOf(prompts)
  const last = prompts.at(-1)
  const arrowsOf = (prompt: QueuedPrompt) =>
    PointerArrowsView($, e, `pointer-up-${prompt.id}`, `pointer-down-${prompt.id}`, () => movePointerUp($, prompts), () => movePointerDown($, prompts))

  return (
    <Box flexDirection="column" rowGap="sm" width="100%">
      {prompts.map((prompt, place) => (
        <Box key={`card-${prompt.id}`} flexDirection="column">
          {CardView($, e, state, prompt, all.indexOf(prompt), place === pointer ? arrowsOf(prompt) : null)}
          {state.openSteps.includes(prompt.id) && (prompt.steps ?? []).length > 0 && StepsView($, e, prompt)}
        </Box>
      ))}
      {last && pointer === prompts.length && (
        <Box key={`pointer-after-${last.id}`} flexDirection="row" paddingLeft={TASK_BUTTON_COLUMNS + 2}>
          {PointerArrowsView($, e, `pointer-up-after-${last.id}`, '', () => movePointerUp($, prompts))}
        </Box>
      )}
    </Box>
  )
}

/** The pointer's column before a step's text: its ▲ and ▼ where the step pointer is, else the same room empty, so no
 * step's text moves. A card's pointer lies over the card's left end instead, as its buttons lie over its right end. */
function PointerColumnView($: EngineInterface, e: AbovePromptEvent, arrows: ReturnType<typeof PointerArrowsView> | null) {
  const { Box } = $.ui.resolve(e)

  return <Box width={POINTER_COLUMNS} flexShrink={0} flexDirection="row" justifyContent="flex-end" alignItems="center">{arrows}</Box>
}

/** The pointer's ▲ and ▼ on a solid grey bar, shown while the pointer is over its card or step, as ↵ ✎ ↑ ↓ ✕ are. */
function PointerArrowsView($: EngineInterface, e: AbovePromptEvent, upKey: string, downKey: string, onUp: () => void, onDown: () => void = () => {}) {
  const elements = $.ui.resolve(e)
  const { Box, Button } = elements

  return (
    <Box flexDirection="row" flexShrink={0} gap={1} backgroundColor={LOOK.popover} borderStyle="round" borderColor={LOOK.popover} paddingX="xs" display="none" hover={{ display: 'flex' }}>
      {upKey !== '' && TipView(elements, upKey, 'Set previous to current', '', <Button key={upKey} label="▲" onPress={onUp} />)}
      {downKey !== '' && TipView(elements, downKey, 'Set next to current', '', <Button key={downKey} label="▼" onPress={onDown} />)}
    </Box>
  )
}

/** One card, the same in the single queue and in a robot's queue: pressing it edits it, and the pointer over it shows
 * its buttons over its right end. */
function CardView($: EngineInterface, e: AbovePromptEvent, state: QueueState, prompt: QueuedPrompt, index: number, pointer: ReturnType<typeof PointerArrowsView> | null) {
  const { Box, Text, Button } = $.ui.resolve(e)
  const isEditing = prompt.id === state.editingId
  const isWorking = pointer !== null
  const progress = progressOf(prompt.steps)
  const isFinished = Boolean(prompt.is_done)

  return (
    <Box key={`card-row-${prompt.id}`} flexDirection="row" justifyContent="space-between" alignItems="center" gap={1} width="100%">
      <Box width={TASK_BUTTON_COLUMNS} flexShrink={0}>
        {progress !== ''
          ? TaskButtonView($, e, `steps-${prompt.id}`, progress, 'Tasks', 'shows or hides them', () => toggleSteps($, prompt.id))
          : TaskButtonView($, e, `steps-${prompt.id}`, '+', 'Add task', 'from the draft in the prompt box', () => addStep($, prompt))}
      </Box>
      {(prompt.attachments ?? []).length > 0 && <Text key={`attached-${prompt.id}`} color={LOOK.muted}>{`📎${prompt.attachments!.length}`}</Text>}
      <Box position="relative" flexGrow={1} flexShrink={1} minWidth={0} flexDirection="row" alignItems="center" paddingX={1}
        backgroundColor={LOOK.card} borderStyle="round" borderColor={isWorking ? LOOK.accent : LOOK.card}>
        <Box flexGrow={1} flexShrink={1} minWidth={0}>
          <Text wrap="truncate-end" color={isEditing ? LOOK.placeholder : isWorking ? LOOK.accent : undefined}
            italic={isEditing} bold={isWorking} underline={isWorking} dimColor={isEditing || isFinished}>
            {`${index + 1}. ${prompt.text.replace(/\s+/g, ' ')}${isEditing ? '  (editing)' : ''}`}
          </Text>
        </Box>
        {PressAreaView($, e, `card-text-${prompt.id}`, CARD_PRESS_AREA, () => editPrompt($, prompt), isEditing || isFinished)}
        {pointer && (
          <Box position="absolute" top={0} bottom={0} left={1} flexDirection="row" alignItems="center">{pointer}</Box>
        )}
        <Box position="relative" width={0} height={0} flexShrink={0} alignSelf="center">
          <Box position="absolute" top={0} bottom={0} left={-CARD_BAR_COLUMNS} flexDirection="row" alignItems="center">
            <Box flexDirection="row" alignItems="center" gap={1}
              display="none" hover={{ display: 'flex' }} backgroundColor={LOOK.popover} borderStyle="round" borderColor={LOOK.popover} paddingX="xs">
              {CardButtonsView($, e, prompt, index)}
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

/** A card's task button, 3/5 or +, centred on a solid grey box the task column's width, so every card's task button
 * is one width whatever its label. */
function TaskButtonView($: EngineInterface, e: AbovePromptEvent, key: string, label: string, words: string, detail: string, onPress: () => void) {
  const elements = $.ui.resolve(e)
  const { Box, Text } = elements

  return (
    <Box key={`${key}-box`} position="relative" width={TASK_BUTTON_COLUMNS} flexDirection="row" justifyContent="center" alignItems="center"
      backgroundColor={LOOK.keyCap} borderStyle="round" borderColor={LOOK.keyCap}>
      <Text>{label}</Text>
      {PressAreaView($, e, key, TASK_PRESS_AREA, onPress)}
      {TipLabelView(elements, words, detail)}
    </Box>
  )
}

/** An invisible button over the whole of a rounded box, so a press anywhere on the box lands: the box draws the shape
 * and the text, the button only takes the press. */
function PressAreaView($: EngineInterface, e: AbovePromptEvent, key: string, area: string, onPress: () => void, dimColor = false) {
  const { Box, Button } = $.ui.resolve(e)

  return (
    <Box position="absolute" top={0} bottom={0} left={0} right={0}>
      <Button key={key} plain label={area} dimColor={dimColor} onPress={onPress} />
    </Box>
  )
}

/** A card's own buttons: send now, edit, move up and down, and remove. */
function CardButtonsView($: EngineInterface, e: AbovePromptEvent, prompt: QueuedPrompt, index: number) {
  const elements = $.ui.resolve(e)
  const { Button } = elements

  return [
    TipView(elements, `send-now-${prompt.id}`, 'Send now', 'sends it to the chat at once', <Button key={`send-now-${prompt.id}`} label="↵" onPress={() => sendNow($, prompt)} />),
    TipView(elements, `edit-${prompt.id}`, 'Edit', 'puts it in the prompt box to change', <Button key={`edit-${prompt.id}`} label="✎" onPress={() => editPrompt($, prompt)} />),
    TipView(elements, `up-${prompt.id}`, 'Move up', '', <Button key={`up-${prompt.id}`} label="↑" onPress={() => movePrompt($, index, index - 1)} />),
    TipView(elements, `down-${prompt.id}`, 'Move down', '', <Button key={`down-${prompt.id}`} label="↓" onPress={() => movePrompt($, index, index + 1)} />),
    TipView(elements, `remove-${prompt.id}`, 'Remove', 'takes it off the queue', <Button key={`remove-${prompt.id}`} label="✕" onPress={() => removePrompt($, prompt.id)} />),
  ]
}

/** Sub-agent mode, in the place of the queue's list: the robots one under another on the left, so many robots read as a
 * plain list, and the open robot's queue to their right, taking the room and the height the robots stand in. */
function AgentColumnsView($: EngineInterface, e: AbovePromptEvent, state: QueueState) {
  const { Box } = $.ui.resolve(e)

  return (
    <Box key="agent-columns" flexDirection="row" gap={1} width="100%">
      <Box key="agent-robots" flexDirection="column" flexShrink={0} rowGap="sm">
        {state.tasks.map((task, place) => AgentRobotView($, e, state, task, place))}
      </Box>
      <Box key="agent-queues" flexDirection="column" flexGrow={1} flexShrink={1} width={0} minWidth={0} rowGap="sm">
        {state.tasks.map((task, place) => AgentQueueView($, e, state, task, place))}
      </Box>
    </Box>
  )
}

/** An open robot's queue: its prompts as the queue's cards, at the full width right of the robots. */
function AgentQueueView($: EngineInterface, e: AbovePromptEvent, state: QueueState, task: SubAgentTask, place: number) {
  if (!state.expandedAgents.includes(place)) {
    return null
  }
  const { Box } = $.ui.resolve(e)
  return (
    <Box key={`agent-column-${place + 1}`} flexDirection="column" width="100%" rowGap="sm">
      {CardsView($, e, state, robotPromptsOf(state.queue.prompts, task, place))}
    </Box>
  )
}

/** One robot on its own line: the robot, which opens its queue to the right and closes it again, its name, and how many
 * of its items are done, such as 3/5, or ✎ to rename it while its queue is open. */
function AgentRobotView($: EngineInterface, e: AbovePromptEvent, state: QueueState, task: SubAgentTask, place: number) {
  const elements = $.ui.resolve(e)
  const { Box, Button, Text } = elements
  const number = place + 1
  const name = agentNameOf(task, place)
  const isOpen = state.expandedAgents.includes(place)
  const items = robotPromptsOf(state.queue.prompts, task, place)
  const picture = 'Svg' in elements
    ? <elements.Svg key={`robot-${number}`} source={robotSvgOf(place)} alt={`${name}, a robot`} width={ROBOT_PIXELS} height={ROBOT_PIXELS} />
    : <Text key={`robot-${number}`} color={LOOK.accent}>🤖</Text>

  return (
    <Box key={`agent-robot-${number}`} flexDirection="row" alignItems="center" gap={1}>
      <Box key={`robot-box-${number}`} flexShrink={0}>
        {picture}
        <Box position="absolute" top={0} left={0}>
          <Button key={`collapse-agent-${number}`} plain label=" " onPress={() => toggleAgentQueue($, place)} />
        </Box>
      </Box>
      <Text bold color={isOpen ? LOOK.accent : LOOK.muted}>{name}</Text>
      {isOpen
        ? TipView(elements, `rename-agent-${number}`, 'Rename', 'names this robot from the prompt box', <Button key={`rename-agent-${number}`} label="✎" onPress={() => renameAgent($, place)} />)
        : <Text key={`agent-progress-${number}`} color={LOOK.muted}>{`${items.filter(item => item.is_done).length}/${items.length}`}</Text>}
    </Box>
  )
}

/** About two lines tall, in the desktop's pixels: a robot stands out over its column. */
const ROBOT_PIXELS = 28

/** A card's steps under it, in order: done ones ticked and dim, the one being worked marked and bright. */
function StepsView($: EngineInterface, e: AbovePromptEvent, prompt: QueuedPrompt) {
  const elements = $.ui.resolve(e)
  const { Box, Button } = elements
  const steps = prompt.steps ?? []
  const pointer = stepPointerOf(steps)
  const up = () => moveStepPointerUp($, prompt)
  const down = () => moveStepPointerDown($, prompt)

  return (
    <Box key={`steps-of-${prompt.id}`} flexDirection="column" paddingLeft={TASK_BUTTON_COLUMNS + 1}>
      {steps.map((step, index) => StepView($, e, prompt, step, index,
        index === pointer ? PointerArrowsView($, e, `step-pointer-up-${prompt.id}`, `step-pointer-down-${prompt.id}`, up, down) : null))}
      <Box flexDirection="row" gap={1}>
        {PointerColumnView($, e, pointer === steps.length ? PointerArrowsView($, e, `step-pointer-up-${prompt.id}`, '', up) : null)}
        {TipView(elements, `add-step-${prompt.id}`, 'Add task', 'from the draft in the prompt box', <Button key={`add-step-${prompt.id}`} label="+" onPress={() => addStep($, prompt)} />)}
      </Box>
    </Box>
  )
}

/** One task under its card: its mark and text, and, with the pointer on it, the card's own buttons for it: ↵ to do it
 * now, ✎ to change it, ↑ ↓ to move it and ✕ to take it off. */
function StepView($: EngineInterface, e: AbovePromptEvent, prompt: QueuedPrompt, step: PromptStep, index: number, pointer: ReturnType<typeof PointerArrowsView> | null) {
  const elements = $.ui.resolve(e)
  const { Box, Button, Text } = elements
  const number = index + 1

  return (
    <Box key={`step-row-${prompt.id}-${number}`} flexDirection="row" justifyContent="space-between" alignItems="center" gap={1}>
      {PointerColumnView($, e, pointer)}
      <Box flexGrow={1} flexShrink={1} minWidth={0}>
        <Text key={`step-${prompt.id}-${number}`} wrap="wrap" dimColor={step.state === 'done'}
          color={step.state === 'in_progress' ? LOOK.accent : undefined}>
          {`${STEP_MARK[step.state]} ${step.text}`}
        </Text>
      </Box>
      <Box flexDirection="row" gap={1} display="none" hover={{ display: 'flex' }} backgroundColor={LOOK.popover} borderStyle="round" borderColor={LOOK.popover} paddingX="xs">
        {TipView(elements, `send-now-step-${prompt.id}-${number}`, 'Send now', 'sends this task to the chat at once', <Button key={`send-now-step-${prompt.id}-${number}`} label="↵" onPress={() => sendStepNow($, prompt, index)} />)}
        {TipView(elements, `edit-step-${prompt.id}-${number}`, 'Edit', 'with the prompt box empty, takes its text; with a draft, replaces it', <Button key={`edit-step-${prompt.id}-${number}`} label="✎" onPress={() => editStep($, prompt, index)} />)}
        {TipView(elements, `up-step-${prompt.id}-${number}`, 'Move up', '', <Button key={`up-step-${prompt.id}-${number}`} label="↑" onPress={() => moveStep($, prompt, index, index - 1)} />)}
        {TipView(elements, `down-step-${prompt.id}-${number}`, 'Move down', '', <Button key={`down-step-${prompt.id}-${number}`} label="↓" onPress={() => moveStep($, prompt, index, index + 1)} />)}
        {TipView(elements, `remove-step-${prompt.id}-${number}`, 'Remove', 'takes this task off', <Button key={`remove-step-${prompt.id}-${number}`} label="✕" onPress={() => removeStep($, prompt, index)} />)}
      </Box>
    </Box>
  )
}
