import type { QueuedPrompt } from '../../types'

/** The queued prompts as the cdd server answered them, in the order they will be sent, as the views draw them. */
export class PromptQueue {
  constructor(readonly prompts: QueuedPrompt[]) {}

  get isEmpty(): boolean {
    return this.prompts.length === 0
  }

  /** The prompts still to do, which the stack's count shows: a done prompt stays on the queue, drawn dim, but is not counted. */
  get size(): number {
    return this.prompts.filter(prompt => !prompt.is_done).length
  }

  get texts(): string[] {
    return this.prompts.map(prompt => prompt.text)
  }

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

// A list item's marker: `1.`, `2)`, `-`, `*` or `•`, with the space after it.
const LIST_MARKER = /^(?:\d+[.)]|[-*•])\s+/

/**
 * The items of a list pasted after `/queue`, in order, each one prompt: the lines that carry a list marker, the marker
 * left off, or every line when none does. A heading among marked items, such as `Session roots setup`, is no item. One
 * line is a focus for planning, not a list, so it answers none.
 */
export function listedItems(text: string): string[] {
  const lines = text.split(/\r?\n/).map(line => line.trim()).filter(line => line !== '')
  if (lines.length < 2) {
    return []
  }
  const marked = lines.filter(line => LIST_MARKER.test(line))

  return (marked.length > 0 ? marked : lines).map(line => line.replace(LIST_MARKER, ''))
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

