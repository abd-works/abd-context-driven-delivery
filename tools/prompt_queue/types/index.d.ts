/** One prompt waiting in the queue, for the agent to do as if the person typed it, as prompt-queue's tools answer it. */
export type QueuedPrompt = { id: string; text: string }

/** The chat's queue as prompt-queue's tools answer it, PromptQueueData in the language adapter, its prompts typed: the
 * contract imports nothing, so the client file checks its answer against the adapter's type. */
export type QueueJson = { chat: string; prompts: QueuedPrompt[] }

/** A failure the queue shows with Fix: what failed with its reason, the context it failed in, and whether Fix is on its way. */
export type QueueFailure = { failure: string; context: string; isFixing?: boolean }

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
    }
  }
}
