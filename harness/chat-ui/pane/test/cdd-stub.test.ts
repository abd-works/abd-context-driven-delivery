import { expect, test } from 'claude-code/testing'

import { cdd } from './cdd-stub'

// The stubbed cdd server answers only the operations Python has, with the arguments Python takes, so a story fails
// when the chat bar calls a name Python dropped, such as board.activate once it became ticket.activate.

// The stub with its engine answers kept by event, so a test can make the call the chat bar's $.mcp.call makes.
function stubbedServer() {
  const answers: Record<string, (context: unknown, event: any) => any> = {}
  const world = cdd((event: string, answer: (context: unknown, event: any) => any) => (answers[event] = answer))
  const call = (tool: string, args: object) => answers['mcp.call'](undefined, { tool, args }).value
  return { world, call }
}

test('should refuse an operation Python does not have', () => {
  const { world, call } = stubbedServer()
  expect(call('board.activate', { ticket: 'checkout-flow' }).isError).toBe(true)
  expect(world.unknown).toEqual(['board.activate is not a cdd operation'])
})

test('should refuse an argument the operation does not take', () => {
  const { world, call } = stubbedServer()
  expect(call('ticket.move_next', { ticket: 'checkout-flow', repo_path: '/' }).isError).toBe(true)
  expect(world.unknown).toEqual(['ticket.move_next takes no argument repo_path'])
})

test('should answer an operation Python has', () => {
  const { world, call } = stubbedServer()
  expect(call('ticket.activate', { ticket: 'checkout-flow', leaving: [], opening: [] }).isError).toBe(false)
  expect(world.unknown).toEqual([])
})
