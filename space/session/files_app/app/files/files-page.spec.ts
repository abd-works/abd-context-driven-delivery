// The Files app's acceptance tests for what only the page shows, story by story as
// space/session/files_app/.context/review-files-in-files-app/review_files_in_files_app_story.test.md writes them; what the
// session answers is proved by space/session/files_app/review-files-in-files-app.story.domain.spec.py.
import { describe, expect, it, vi } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { PracticeSessionOutputData } from '@cdd/space/session/practice-session-output'

import { FilesLink } from './files-link'
import { FilesPage, filesShown, PRACTICES_REFRESH_MILLISECONDS, type DrawioTab } from './files-page'

// The Files app's page against a fake of its own server: each post answers what the route would, and is kept in order.
class FakeFilesServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = []
  readonly practices: Record<string, PracticeSessionOutputData> = {
    stories: practice('stories', 'Stories', '#c0392b', true),
    ddd: practice('ddd', 'DDD', '#2471a3', false),
  }

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    if (path.endsWith('/show')) return { name: 'release-2', session_file: SESSION, practices: this.practices } as Result
    if (path.endsWith('/enable')) {
      const name = decodeURIComponent(path.split('/')[3] ?? '')
      this.practices[name] = { ...this.practices[name]!, enabled: Boolean(body.is_enabled) }
      return this.practices[name] as Result
    }
    if (path.endsWith('/files')) return { markdown: [entry(`.context/${path.split('/')[3]}.md`)] } as Result
    if (path.endsWith('/drawio/open')) return { url: 'http://127.0.0.1:8791/edit?f=a.drawio' } as Result
    return null
  }

  posted(ending: string): { path: string; body: Record<string, unknown> }[] {
    return this.posts.filter(post => post.path.endsWith(ending))
  }
}

const SESSION = '.sessions/release-2/session.json'

function practice(name: string, short_name: string, colour: string, enabled: boolean): PracticeSessionOutputData {
  const fidelity_slugs = { stories: ['stories-story-map'], ddd: ['ddd-bounded-context'] }[name] ?? []
  return { name, short_name, colour, fidelity_slugs, enabled, session_file: SESSION, design_view: '', root: '', is_root_chosen: false }
}

function entry(path: string) {
  return { path, exists: true, is_changed: false } as never
}

const STAGE_LINK = '?files=release-2&fidelity=stories-story-map,ddd-bounded-context&chat=chat-1'

class FakeTab implements DrawioTab {
  location = { href: '' }
  isClosed = false
  close(): void {
    this.isClosed = true
  }
}

async function settled(): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 0))
}

describe('Toggle Practice In Files App', () => {
  describe('with a stage of two practices, one turned off', () => {
    it('should show a toggle for each practice, on or off', async () => {
      const page = new FilesPage(new FakeFilesServer(), new FilesLink(STAGE_LINK))
      await page.readPractices()
      expect(page.state.practices.map(each => `${each.short_name}:${each.enabled}`)).toEqual(['Stories:true', 'DDD:false'])
    })

    it('should list only the files of the practice turned on', () => {
      const shown = filesShown(
        [
          { slug: 'stories-story-map', entries: [entry('.context/story-map.md')] },
          { slug: 'ddd-bounded-context', entries: [entry('.context/bounded-context-map.md')] },
        ],
        Object.values(new FakeFilesServer().practices),
      )
      expect(shown.map(each => (each as { path: string }).path)).toEqual(['.context/story-map.md'])
    })

    describe('that has the practice turned off pressed', () => {
      it('should turn it on for the session', async () => {
        const server = new FakeFilesServer()
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await page.readPractices()
        await page.togglePractice('ddd')
        expect(server.practices.ddd!.enabled).toBe(true)
      })

      // Keep Chat Bar Practices In Sync
      it('should tell the chat that opened the page to read the board again, so its chat bar shows it on', async () => {
        const server = new FakeFilesServer()
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await page.readPractices()
        await page.togglePractice('ddd')
        expect(server.posted('/send')).toEqual([{ path: '/chat/chat-1/send', body: { kind: 'refresh', text: 'practices' } }])
      })
    })

    // Keep Chat Bar Practices In Sync
    describe('that has the practice turned on, turned off on the chat bar', () => {
      it('should hide its files while the page shows, with no press here', async () => {
        vi.useFakeTimers()
        try {
          const server = new FakeFilesServer()
          const page = new FilesPage(server, new FilesLink(STAGE_LINK))
          const stop = page.start()
          await vi.advanceTimersByTimeAsync(0)
          server.practices.stories = { ...server.practices.stories!, enabled: false }
          await vi.advanceTimersByTimeAsync(PRACTICES_REFRESH_MILLISECONDS)
          stop()
          expect(page.state.entries.map(each => (each as { path: string }).path)).toEqual([])
        } finally {
          vi.useRealTimers()
        }
      })
    })
  })
})

describe('Open Diagram In Draw.io Tab', () => {
  describe('with a .drawio file pressed', () => {
    it('should send a tab opened during the press to the draw.io viewer, leaving this tab on the file list', async () => {
      const tab = new FakeTab()
      const page = new FilesPage(new FakeFilesServer(), new FilesLink(STAGE_LINK), () => tab)
      const opening = page.open('a.drawio')
      expect(tab.location.href).toBe('')
      await opening
      await settled()
      expect(tab.location.href).toBe('http://127.0.0.1:8791/edit?f=a.drawio')
    })

    it('should close the tab when the viewer does not open', async () => {
      const tab = new FakeTab()
      const failing = new FakeFilesServer()
      failing.post = async () => {
        throw new Error('the viewer did not start')
      }
      const page = new FilesPage(failing, new FilesLink(STAGE_LINK), () => tab)
      await page.open('a.drawio')
      expect(tab.isClosed).toBe(true)
    })
  })
})
