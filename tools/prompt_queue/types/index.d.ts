/** One prompt waiting in the queue, sent as if the person typed it. */
export type QueuedPrompt = { id: string; text: string }

/** One task a sub-agent runs: the queued prompts the model grouped together. */
export type SubAgentTask = { description: string; prompts: string[] }

declare module 'claude-code' {
  interface PluginState {
    'prompt-queue': {
      prompts: QueuedPrompt[]
      isExpanded: boolean
      isSubAgentMode: boolean
      tasks: SubAgentTask[]
      notice: string
      queuedByKey: string
      isPlaying: boolean
      isTurnRunning: boolean
    }
  }
}
