import { describe, expect, it } from 'vitest'

import { ClaudeLink } from './claude-link'

const NEW_CHAT = 'claude://code/new?folder=C%3A%5Cdev%5Cpets&q=Title%20this%20session%20%22pet-visits%22'

const launched = (): { calls: string[][]; link: ClaudeLink } => {
  const calls: string[][] = []
  return { calls, link: new ClaudeLink((command, args) => calls.push([command, ...args])) }
}

describe("Open a ticket's new chat in the Claude app", () => {
  it('should hand the new-chat link to the system whole', () => {
    const { calls, link } = launched()
    link.open(NEW_CHAT)
    expect(calls[0]?.at(-1)).toBe(NEW_CHAT)
  })

  it('should refuse a link that is not a new chat', () => {
    const { link } = launched()
    expect(() => link.open('https://example.com')).toThrow('Refused')
  })

  it('should open nothing for a refused link', () => {
    const { calls, link } = launched()
    expect(() => link.open('claude://settings')).toThrow()
    expect(calls).toEqual([])
  })
})
