// Which checkout an app's page opens on: the chat bar opens the board, the Files app and the Graph on the checkout the
// chat works in (checkoutFolder, board.ts), so the cdd server answers a ticket's worktree on the dev lane and the main
// checkout on the stable lane. Run through /board, which answers where the board is.
import { expect, test } from 'claude-code/testing'

import { PROJECT_QUERY } from './board'

// Seed: a ticket's worktree, as git names the top of the checkout a chat works in.
const WORKTREE = 'C:/dev/abd-cdd-file-manager'
// Seed: the board, running, as app.open answers it.
const BOARD = { label: 'Kanban', status: 'running', port: 9778, url: 'http://127.0.0.1:9778/', server: { folder: 'C:/cdd/kanban', command: ['node', 'serve.ts'] } }

type TestOn = Parameters<Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>>[1]

/** The chat's engine: its session, the cdd server answering the board as running, and git answering the top of the
 * checkout, or failing outside any repository. Answers the commands git was asked. */
function chatIn(on: TestOn, top: string | null): string[][] {
  const ran: string[][] = []
  on('session.root', () => ({ value: WORKTREE }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('mcp.call', () => ({ value: { content: [{ type: 'text', text: JSON.stringify(BOARD) }], isError: false } }))
  on('process.run', (_, e) => {
    ran.push((e as { argv: string[] }).argv)
    return { value: top === null ? { exitCode: 128, stdout: '', stderr: 'fatal: not a git repository' } : { exitCode: 0, stdout: `${top}\n`, stderr: '' } }
  })
  return ran
}

const boardAddress = (answer: { text?: string }): URL => new URL((answer.text ?? '').replace(/^The board is at /, '').replace(/\.$/, ''))

test("the board opens on the checkout git names as the chat's own", async ($, on) => {
  const ran = chatIn(on, WORKTREE)

  const answer = await $.command.run({ command: 'board', args: '' })

  expect([boardAddress(answer).searchParams.get(PROJECT_QUERY), ran]).toEqual([WORKTREE, [['git', 'rev-parse', '--show-toplevel']]])
})

// Reported 2026-11-18: a project that is no git repository opened the Files app on the server's own project, which
// holds none of its tickets or sessions.
test('the board opened outside any repository opens on the folder the chat works in', async ($, on) => {
  chatIn(on, null)

  const answer = await $.command.run({ command: 'board', args: '' })

  expect(boardAddress(answer).searchParams.get(PROJECT_QUERY)).toBe(WORKTREE)
})
