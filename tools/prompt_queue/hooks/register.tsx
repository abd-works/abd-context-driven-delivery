import type { Register } from 'claude-code'

import {
  currentQueue,
  isQueuedByKey,
  queueFromCommand,
  queueByKey,
  queueContext,
  refreshQueue,
  finishTurn,
  startTurn,
} from './queue/prompt-queue'
import { QueueView } from './queue/queue-view'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'queue',
      description: 'Queue a pasted list, one prompt per item, or turn this conversation into ordered prompts',
      argumentHint: '[a list to queue, or what to focus on]',
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
      return { drop: 'Queued for later' }
    }
    const queued = e.command ? undefined : await queueContext($)

    return next(queued ? { ...e, context: [...(e.context ?? []), queued] } : e)
  })

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

    return QueueView($, e, await currentQueue($))
  })
}
