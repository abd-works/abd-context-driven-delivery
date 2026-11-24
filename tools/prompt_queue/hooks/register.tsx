import type { Register } from 'claude-code'

import {
  currentQueue,
  isQueuedByKey,
  keepQueuedAttachments,
  queueFromCommand,
  queueByKey,
  queueContext,
  queueSentPrompt,
  followPlan,
  followTakenPrompt,
  finishPlan,
  noteDecisionAsked,
  refreshQueue,
  finishTurn,
  startRobotAgent,
  startTurn,
  followQueueAnswer,
} from './queue/prompt-queue'
import { QueueView } from './queue/queue-view'
import { PLAN_TOOL, PROMPT_QUEUE_TOOL, SET_STEPS_TOOL, WRAP_UP_TOOL } from './queue/plan-steps'

/** Whether a tool call's answer says the call failed, such as the server refusing a prompt it does not hold. */
function isRefused(ran: unknown): boolean {
  return Boolean((ran as { result?: { isError?: boolean } } | undefined)?.result?.isError)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'queue',
      description: 'Queue a pasted list, one prompt per item; place a draft into the plan; or, with nothing given, turn this conversation into ordered prompts',
      argumentHint: '[a list to queue, or a draft to place into the plan]',
    })
    // The queue lives on the cdd server: the agent or a session starting in this chat may already have queued prompts.
    await refreshQueue($)

    return next(e)
  })

  on('command.run', { command: 'queue' }, async ($, e) => {
    return { text: await queueFromCommand($, e.args) }
  })

  // Alt+Enter queues the draft instead of sending it; the engine reports Alt as meta. Ctrl+Enter never reached a mod
  // on the desktop.
  on('prompt.edit', async ($, e, next) => {
    if (e.key?.key !== 'return' || !(e.key.meta || e.key.ctrl)) {
      return next(e)
    }
    await queueByKey($, e.text)

    return { text: '', cursor: 0 }
  })

  // The desktop may still submit the draft after the key that queued it; it is queued, so it does not enter now.
  // Every other prompt carries the queue beside it while the queue plays, so the agent takes its work in order.
  on('prompt.submit', async ($, e, next) => {
    if (e.origin?.kind !== 'plugin' && (await isQueuedByKey($, e.text))) {
      await keepQueuedAttachments($, e.text, e.attachments ?? [])
      return { drop: 'Queued for later' }
    }
    const sent = e.command || e.origin?.kind === 'plugin' ? undefined : await queueSentPrompt($, e.text)
    const queued = e.command ? undefined : await queueContext($, sent?.id)
    const added = [sent?.note, queued].filter((block): block is string => block !== undefined)

    return next(added.length > 0 ? { ...e, context: [...(e.context ?? []), ...added] } : e)
  })

  // The agent's task list in the chat is copied onto the prompt it works on, so the queue shows its steps.
  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (PROMPT_QUEUE_TOOL.test(e.tool) && !isRefused(ran)) {
      await followQueueAnswer($, ran)
    }
    if (e.agentId === undefined && PLAN_TOOL.test(e.tool)) {
      await followPlan($, e as unknown as Record<string, unknown>)
    } else if (e.agentId === undefined && SET_STEPS_TOOL.test(e.tool) && !isRefused(ran)) {
      await followTakenPrompt($, e as unknown as Record<string, unknown>)
    } else if (e.agentId === undefined && WRAP_UP_TOOL.test(e.tool)) {
      await finishPlan($)
      await noteDecisionAsked($, e as unknown as Record<string, unknown>)
    }

    return ran
  })

  // A sub-agent this chat starts for a robot goes by that robot's name, so the robot and its background task match.
  on('agent.spawn', async ($, e, next) => (e.parentAgentId === undefined ? startRobotAgent($, e, next) : next(e)))

  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) {
      await startTurn($)
    }

    return next(e)
  })

  // Playing, a finished main-chat turn asks the agent to take the next prompt, ahead of Claude's own queue.
  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId === undefined) {
      await finishTurn($, e.reason === 'answer')
    }

    return result
  })

  // The queue's box goes first in the band, so it sits above the chat bar rather than among its rows.
  on('ui.render', { component: 'AbovePromptList' }, ($, e, next) => {
    const isQueue = (row: { plugin: string }) => row.plugin === 'prompt-queue'
    const rows = [...e.props.rows.filter(isQueue), ...e.props.rows.filter(row => !isQueue(row))]

    return next({ ...e, props: { ...e.props, rows } })
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) {
      return next(e)
    }

    try {
      return QueueView($, e, await currentQueue($))
    } catch (failure) {
      // A draw that throws shows why, in red, as the chat bar's does, instead of leaving no queue at all.
      const { Text } = $.ui.resolve(e)
      const reason = failure instanceof Error ? `${failure.message}\n${failure.stack ?? ''}` : String(failure)
      return <Text color="#EF4444">{`prompt queue failed to draw: ${reason}`}</Text>
    }
  })
}
