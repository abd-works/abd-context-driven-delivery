// Send A Failure To Be Fixed, as the page shows it: what Python answers for a failure (its causes and its fix command)
// is proved by tools/error_display/failure_spec.py, and the page on its real server by
// story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/send-failure-to-be-fixed.story.ui_e2e_spec.py.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { SessionFileData } from '@cdd/space/session/session'

import { FilesNotices } from './files-notices'
import { FilesStore } from './files-state'

const NOT_OPENED = 'The Files app did not open src/order.py: nothing at src/order.py'
const OPENING = 'Opening src/order.py in the Files app, calling session.file'
const CAUSES = ['The file was moved, renamed or deleted after the page listed it.', 'The file sits outside the roots of the session.']
const FIX_COMMAND = '/space-session-debug-session choice=fix details="Failure: ..."'
const CHECKOUT_CHAT = 'checkout-chat'
const NO_POLICY = '.context/returns-policy.md is not there'
const NO_HEADING = '.context/domain-model.md has no heading #cart'

// The Files server as the page calls it: failure.describe answers the causes Python holds for the kind, and chat.send
// is kept, or refused while the chat is not connected.
class FakeFilesServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = []
  isChatConnected = true

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    if (path === '/failure/describe') return { failure: body.failure, context: body.context, kind: body.kind, causes: body.kind ? CAUSES : [], fix_command: FIX_COMMAND } as Result
    if (path.endsWith('/send') && !this.isChatConnected) throw new Error(`the chat ${CHECKOUT_CHAT} is not connected`)
    return null
  }

  get sent(): Record<string, unknown>[] {
    return this.posts.filter(post => post.path === `/chat/${CHECKOUT_CHAT}/send` && post.body.kind === 'command').map(post => post.body)
  }
}

function page(chat = CHECKOUT_CHAT) {
  const server = new FakeFilesServer()
  const store = new FilesStore()
  const notices = new FilesNotices(store, server, chat)
  return { server, store, notices, fixes: notices.fixes }
}

const storyMap = (...missing: string[]): SessionFileData => ({ path: '.context/story-map.md', callouts: missing.map((each, line) => ({ line, title: '', link: '', section: null, missing: each })) }) as unknown as SessionFileData

describe('a failure the Files app shows', () => {
  describe('that the page met opening a file', () => {
    it('should stay on the page with its context and its kind', () => {
      const { store, notices } = page()
      notices.fail(NOT_OPENED, OPENING, { kind: 'file_display' })
      expect(store.state.failures.map(({ failure, context, kind, fix }) => ({ failure, context, kind, fix }))).toEqual([{ failure: NOT_OPENED, context: OPENING, kind: 'file_display', fix: 'not_asked' }])
    })

    it('should show once however often the page meets it', () => {
      const { store, notices } = page()
      notices.fail(NOT_OPENED, OPENING, { kind: 'file_display' })
      notices.fail(NOT_OPENED, OPENING, { kind: 'file_display' })
      expect(store.state.failures).toHaveLength(1)
    })

    it('should leave the page once dismissed', () => {
      const { store, fixes } = page()
      fixes.show(NOT_OPENED, OPENING, 'file_display')
      fixes.dismiss(NOT_OPENED)
      expect(store.state.failures).toEqual([])
    })
  })

  describe('with Fix pressed', () => {
    async function fixed(chat = CHECKOUT_CHAT, isChatConnected = true) {
      const opened = page(chat)
      opened.server.isChatConnected = isChatConnected
      opened.fixes.show(NOT_OPENED, OPENING, 'file_display')
      await opened.fixes.fix(NOT_OPENED)
      return { ...opened, shown: opened.store.state.failures[0]! }
    }

    it('should ask Python for the causes of its kind', async () => {
      const { server } = await fixed()
      expect(server.posts[0]).toEqual({ path: '/failure/describe', body: { failure: NOT_OPENED, context: OPENING, kind: 'file_display' } })
    })

    it('should list the most common causes Python answered', async () => {
      expect((await fixed()).shown.described?.causes).toEqual(CAUSES)
    })

    it('should send the chat that opened the page the fix command Python answered', async () => {
      expect((await fixed()).server.sent).toEqual([{ kind: 'command', text: FIX_COMMAND }])
    })

    it('should say the fix was sent', async () => {
      expect((await fixed()).shown.fix).toBe('sent')
    })

    describe('on a page no chat opened', () => {
      it('should send nothing', async () => {
        expect((await fixed('')).server.posts.map(post => post.path)).toEqual(['/failure/describe'])
      })

      it('should say to copy the command into a chat', async () => {
        expect((await fixed('')).shown.note).toBe('No chat opened this page, so nothing was sent: copy the command into a chat to have it fixed.')
      })

      it('should keep the command to show', async () => {
        expect((await fixed('')).shown.described?.fix_command).toBe(FIX_COMMAND)
      })
    })

    describe('with a chat that is not connected', () => {
      it('should say why the fix did not reach the chat', async () => {
        expect((await fixed(CHECKOUT_CHAT, false)).shown.note).toBe(`The fix did not reach the chat: the chat ${CHECKOUT_CHAT} is not connected`)
      })

      it('should offer Fix again', async () => {
        expect((await fixed(CHECKOUT_CHAT, false)).shown.fix).toBe('not_sent')
      })
    })
  })

  describe('that is a link of the open file leading nowhere', () => {
    it('should say each link that is missing as one failure of the file', () => {
      const { store, fixes } = page()
      fixes.showMissingLinksOf(storyMap(NO_POLICY, NO_HEADING))
      expect(store.state.failures.map(({ failure, kind }) => ({ failure, kind }))).toEqual([{ failure: `.context/story-map.md has 2 links that lead nowhere: ${NO_POLICY}; ${NO_HEADING}`, kind: 'missing_link' }])
    })

    it('should show no failure for a file whose every link leads somewhere', () => {
      const { store, fixes } = page()
      fixes.showMissingLinksOf(storyMap())
      expect(store.state.failures).toEqual([])
    })

    it('should say only what the latest read of the file answered', () => {
      const { store, fixes } = page()
      fixes.showMissingLinksOf(storyMap(NO_POLICY, NO_HEADING))
      fixes.showMissingLinksOf(storyMap(NO_POLICY))
      expect(store.state.failures.map(shown => shown.failure)).toEqual([`.context/story-map.md has a link that leads nowhere: ${NO_POLICY}`])
    })

    it('should stay dismissed while the file is read again', () => {
      const { store, fixes } = page()
      fixes.showMissingLinksOf(storyMap(NO_POLICY))
      fixes.dismiss(store.state.failures[0]!.failure)
      fixes.showMissingLinksOf(storyMap(NO_POLICY))
      expect(store.state.failures).toEqual([])
    })
  })
})
