/** One prompt waiting in the queue, for the agent to do as if the person typed it, as prompt-queue's tools answer it. */
/** is_done: its work is done; it stays in its place, drawn dim, until the queue is cleared. robot: the sub-agent it is given to.
 * is_waiting: it waits to be done, neither done nor asking a decision, so the queue's pointer may stand on it.
 * step_pointer: the place, from 0, of its first step not done, where its steps' pointer stands. */
export type QueuedPrompt = { id: string; text: string; steps?: PromptStep[]; attachments?: string[]; is_done?: boolean; robot?: string; is_waiting?: boolean; step_pointer?: number }

/** Where a step of a queued prompt stands, as prompt-queue's tools answer it. */
export type StepState = 'pending' | 'in_progress' | 'done'

/** One thing the agent planned for a queued prompt: its text and where it stands. */
export type PromptStep = { text: string; state: StepState }

/** is_on: whether the person switched the queue on for the chat; off, the mod leaves the chat alone. */
/** The chat's queue as prompt-queue's tools answer it, PromptQueueData in the language adapter, its prompts typed: the
 * contract imports nothing, so the client file checks its answer against the adapter's type. */
export type QueueJson = { chat: string; prompts: QueuedPrompt[]; next?: { id: string } | null; is_on?: boolean }

/** The queue's latest failure, which CDD's shared failure line shows: what failed with its reason, the context it failed
 * in, and its number, which grows with each failure so a newer one shows after an older one was handled. */
export type QueueFailure = { id: number; failure: string; context: string }

/** One task a sub-agent runs: the queued prompts the model grouped together. */
/** name: what the person called the sub-agent; until then it goes by a fun name for its place. */
export type SubAgentTask = { description: string; prompts: string[]; name?: string }

declare module 'claude-code' {
  interface PluginState {
    'prompt-queue': {
      queue: QueueJson
      isExpanded: boolean
      isSubAgentMode: boolean
      tasks: SubAgentTask[]
      notice: string
      failure: QueueFailure | null
      queuedByKey: string
      isPlaying: boolean
      isTurnRunning: boolean
      editingId: string
      askedAbout: string
      plan: PromptStep[]
      isPlanSeen: boolean
      openSteps: string[]
      expandedAgents: number[]
      sentCards: Record<string, string>
      robotAgents: Record<string, string>
      isAwaitingDecision: boolean
      decisionWait: number
      // The cdd server that answered the queue's last call, asked first next time; empty before any answered.
      answeringServer: string
    }
  }
}
