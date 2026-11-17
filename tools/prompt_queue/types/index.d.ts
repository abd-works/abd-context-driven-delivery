/** One prompt waiting in the queue, for the agent to do as if the person typed it, as prompt-queue's tools answer it. */
export type QueuedPrompt = { id: string; text: string; steps?: PromptStep[]; attachments?: string[] }

/** Where a step of a queued prompt stands, as prompt-queue's tools answer it. */
export type StepState = 'pending' | 'in_progress' | 'done'

/** One thing the agent planned for a queued prompt: its text and where it stands. */
export type PromptStep = { text: string; state: StepState }

/** The chat's queue as prompt-queue's tools answer it, PromptQueueData in the language adapter, its prompts typed: the
 * contract imports nothing, so the client file checks its answer against the adapter's type. */
export type QueueJson = { chat: string; prompts: QueuedPrompt[] }

/** The queue's latest failure, which CDD's shared failure line shows: what failed with its reason, the context it failed
 * in, and its number, which grows with each failure so a newer one shows after an older one was handled. */
export type QueueFailure = { id: number; failure: string; context: string }

/** One task a sub-agent runs: the queued prompts the model grouped together. */
export type SubAgentTask = { description: string; prompts: string[] }

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
    }
  }
}
