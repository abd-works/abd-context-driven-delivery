import type { QueuedPrompt } from '../../types'

/** The queued prompts in the order they will be sent; each change answers a new queue. */
export class PromptQueue {
  constructor(readonly prompts: QueuedPrompt[]) {}

  get first(): QueuedPrompt | undefined {
    return this.prompts[0]
  }

  get isEmpty(): boolean {
    return this.prompts.length === 0
  }

  get size(): number {
    return this.prompts.length
  }

  get texts(): string[] {
    return this.prompts.map(prompt => prompt.text)
  }

  withAdded(text: string): PromptQueue {
    return new PromptQueue([...this.prompts, { id: newPromptId(), text }])
  }

  withMoved(from: number, to: number): PromptQueue {
    const last = this.prompts.length - 1
    if (from < 0 || from > last || from === to) {
      return this
    }
    const reordered = [...this.prompts]
    const [moved] = reordered.splice(from, 1)
    reordered.splice(Math.max(0, Math.min(to, last)), 0, moved as QueuedPrompt)

    return new PromptQueue(reordered)
  }

  /** The queue with promptId's text changed in its place, so editing a prompt never moves it. */
  withText(promptId: string, text: string): PromptQueue {
    return new PromptQueue(this.prompts.map(prompt => (prompt.id === promptId ? { ...prompt, text } : prompt)))
  }

  /** The first prompt that may be sent: one being edited waits in its place until it is queued again. */
  firstExcept(promptId: string): QueuedPrompt | undefined {
    return this.prompts.find(prompt => prompt.id !== promptId)
  }

  has(promptId: string): boolean {
    return this.prompts.some(prompt => prompt.id === promptId)
  }

  without(id: string): PromptQueue {
    return new PromptQueue(this.prompts.filter(prompt => prompt.id !== id))
  }
}

function newPromptId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

/** The first JSON array in a model's reply, or none when the reply holds no array. */
export function parseJsonArray(reply: string): unknown[] {
  const start = reply.indexOf('[')
  const end = reply.lastIndexOf(']')
  if (start < 0 || end <= start) {
    return []
  }
  const parsed: unknown = JSON.parse(reply.slice(start, end + 1))

  return Array.isArray(parsed) ? parsed : []
}

/** A queued prompt that is a slash command, `/name args`, split as the engine runs it; none for any other text. */
export function slashCommandOf(text: string): { command: string; args: string } | undefined {
  const typed = text.trim()
  if (!typed.startsWith('/')) {
    return undefined
  }
  const space = typed.search(/\s/)
  if (space < 0) {
    return { command: typed.slice(1), args: '' }
  }

  return { command: typed.slice(1, space), args: typed.slice(space + 1).trim() }
}

