// The band's pure rules for + waiting on an empty prompt box (hooks/queue/awaited-task.ts). The band itself runs only in
// Claude Code's plugin tests (hooks/register.test.tsx); these run under vitest with globals, beside the band, not in it.
import { EMPTY_TASK_NOTICE, isTaskAwaited, noticeAfterChange, personsWords } from './hooks/queue/awaited-task'

describe('+ waiting for a task on an empty prompt box', () => {
  describe('that the queue changes while it waits', () => {
    it('keeps the hint shown, so the person still sees the next message becomes the task', () => {
      expect(noticeAfterChange(EMPTY_TASK_NOTICE)).toBe(EMPTY_TASK_NOTICE)
    })

    it('clears any other notice, as every change of the queue does', () => {
      expect(noticeAfterChange('Paused: the agent left "a" on the queue. Press play to ask again.')).toBe('')
    })
  })

  it('takes the message while the hint shows and the queue is on', () => {
    expect(isTaskAwaited('a', EMPTY_TASK_NOTICE, true)).toBe(true)
  })

  it('takes no message once the hint is gone, since a wait the person cannot see has ended', () => {
    expect(isTaskAwaited('a', '', true)).toBe(false)
  })

  it('takes no message once the queue is switched off', () => {
    expect(isTaskAwaited('a', EMPTY_TASK_NOTICE, false)).toBe(false)
  })

  it('takes no message when + waits on no card', () => {
    expect(isTaskAwaited('', EMPTY_TASK_NOTICE, true)).toBe(false)
  })
})

// The state the Claude app puts before a message sent while a board viewer is open: the viewer's, not the person's.
const VIEWER_STATE = '<artifact-view-context artifact="c9a2df8e">\n{"context":{"mode":"board"}}\n</artifact-view-context>'

describe('the task a message sent while + waits becomes', () => {
  it("is only the person's words, the board viewer's state left out", () => {
    expect(personsWords(`${VIEWER_STATE} make the header blue`)).toBe('make the header blue')
  })

  it("is nothing for a message that holds only a board viewer's state", () => {
    expect(personsWords(VIEWER_STATE)).toBe('')
  })
})
