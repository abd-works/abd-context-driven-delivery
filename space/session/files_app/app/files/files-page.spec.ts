// The Files app's acceptance tests for what only the page shows, story by story as
// space/session/files_app/.context/review-files-in-files-app/review_files_in_files_app_story.test.md writes them; what the
// session answers is proved by space/session/files_app/review-files-in-files-app.story.domain.spec.py.
import { describe, expect, it, vi } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { PracticeSessionOutputData } from '@cdd/space/session/practice-session-output'

import { FilesLink } from './files-link'
import { FilesPage, filesShown, PRACTICES_REFRESH_MILLISECONDS } from './files-page'
import { drawioPageOf } from './files-paths'

// The Files app's page against a fake of its own server: each post answers what the route would, and is kept in order.
class FakeFilesServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = []
  // The fidelities the opening chat's chat bar has selected, as it said at its last check-in.
  selected: string[] = []
  // The stages cdd holds for the chat: each with its fidelities, and those shown; none shown, the link's stage.
  stages: Record<string, string[]> = {}
  shownStages: string[] = []
  isStageChosen = false
  // The session's format chips for the page's fidelities, markdown and diagram, none chosen.
  formats = [
    { label: 'markdown', formats: ['markdown'], offered: 2, made: 2, is_chosen: false },
    { label: 'diagram', formats: ['drawio'], offered: 2, made: 1, is_chosen: false },
  ]
  readonly practices: Record<string, PracticeSessionOutputData> = {
    stories: practice('stories', 'Stories', '#c0392b', true),
    ddd: practice('ddd', 'DDD', '#2471a3', false),
  }

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    if (path.endsWith('/format-choices')) return this.formats as Result
    if (path.endsWith('/choose-formats')) {
      this.formats = this.formats.map(chip => (chip.label === body.label ? { ...chip, is_chosen: Boolean(body.is_chosen) } : chip))
      return this.formats as Result
    }
    if (path.startsWith('/chat/') && path.endsWith('/select')) this.selected = [...(body.selected_fidelities as string[])]
    if (path.startsWith('/chat/') && path.endsWith('/show-stages')) {
      this.shownStages = [...(body.shown_stages as string[])]
      this.isStageChosen = true
    }
    if (path.startsWith('/chat/') && (path.endsWith('/show') || path.endsWith('/select') || path.endsWith('/show-stages'))) return { id: 'chat-1', name: 'release-2', is_busy: false, folder: '', selected_fidelities: this.selected, shown_stages: this.shownStages, stages: this.stages, is_stage_chosen: this.isStageChosen } as Result
    if (path.endsWith('/show')) return { name: 'release-2', session_file: SESSION, practices: this.practices } as Result
    if (path.endsWith('/enable')) {
      const name = decodeURIComponent(path.split('/')[3] ?? '')
      this.practices[name] = { ...this.practices[name]!, enabled: Boolean(body.is_enabled) }
      return this.practices[name] as Result
    }
    if (path.endsWith('/files')) return { markdown: [entry(`.context/${path.split('/')[3]}.md`)], drawio: [entry(`.context/${path.split('/')[3]}.drawio`)] } as Result
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


async function settled(): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 0))
}

// The page as the person finds it once it opened: its files listed and the session's practices read.
async function started(page: FilesPage): Promise<void> {
  page.start()()
  await settled()
}

describe('Toggle Practice In Files App', () => {
  describe('with a stage of two practices, one turned off', () => {
    it('should show a toggle for each practice, on or off', async () => {
      const page = new FilesPage(new FakeFilesServer(), new FilesLink(STAGE_LINK))
      await started(page)
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
        await started(page)
        await page.togglePractice('ddd')
        expect(server.practices.ddd!.enabled).toBe(true)
      })

      // Keep Chat Bar Practices In Sync
      it('should tell the chat that opened the page to read the board again, so its chat bar shows it on', async () => {
        const server = new FakeFilesServer()
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await started(page)
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
  describe('with a .drawio file listed', () => {
    it("should link it to the Files server's draw.io page, which sends a tab of its own to the viewer", () => {
      expect(drawioPageOf('C:/dev/work/.context/a.drawio', 'chat-1')).toBe('/api/drawio/page?path=C%3A%2Fdev%2Fwork%2F.context%2Fa.drawio&chat=chat-1')
    })

    it('should leave this tab on its file list once pressed', async () => {
      const page = new FilesPage(new FakeFilesServer(), new FilesLink(STAGE_LINK))
      await started(page)
      const shown = page.state.openPath
      await page.open('.context/stories-story-map.drawio')
      expect(page.state.openPath).toBe(shown)
    })
  })
})

describe('Follow Chat Bar Selection In Files App', () => {
  describe('with a stage of two practices, both turned on', () => {
    describe('that has the DDD dot selected on the chat bar', () => {
      async function followingDdd(): Promise<FilesPage> {
        const server = new FakeFilesServer()
        server.practices.ddd = practice('ddd', 'DDD', '#2471a3', true)
        server.selected = ['ddd-bounded-context']
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await started(page)
        return page
      }

      it("should list only the selected fidelity's files", async () => {
        const page = await followingDdd()
        expect(page.state.entries.map(each => each.path)).toEqual(['.context/ddd-bounded-context.md', '.context/ddd-bounded-context.drawio'])
      })

      it("should show the selected fidelity's practice on and the other off", async () => {
        const page = await followingDdd()
        expect(page.state.practices.map(each => `${each.short_name}:${page.isShown(each)}`)).toEqual(['Stories:false', 'DDD:true'])
      })
    })

    describe('that has Stories pressed in the Files app', () => {
      async function pressedStories(): Promise<{ page: FilesPage; server: FakeFilesServer }> {
        const server = new FakeFilesServer()
        server.practices.ddd = practice('ddd', 'DDD', '#2471a3', true)
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await started(page)
        await page.togglePractice('stories')
        return { page, server }
      }

      it("should select the other practice's fidelity for the chat, which its chat bar's dots show", async () => {
        const { server } = await pressedStories()
        expect(server.selected).toEqual(['ddd-bounded-context'])
      })

      it("should list only the other practice's files", async () => {
        const { page } = await pressedStories()
        expect(page.state.entries.map(each => each.path)).toEqual(['.context/ddd-bounded-context.md', '.context/ddd-bounded-context.drawio'])
      })

      it('should clear the selection once pressed again, every practice shown', async () => {
        const { page, server } = await pressedStories()
        await page.togglePractice('stories')
        expect(server.selected).toEqual([])
      })
    })

    describe('that has the selection cleared on the chat bar', () => {
      it('should list the files of every practice turned on again', async () => {
        vi.useFakeTimers()
        const server = new FakeFilesServer()
        server.practices.ddd = practice('ddd', 'DDD', '#2471a3', true)
        server.selected = ['ddd-bounded-context']
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        page.start()
        await vi.advanceTimersByTimeAsync(0)
        server.selected = []
        await vi.advanceTimersByTimeAsync(PRACTICES_REFRESH_MILLISECONDS)
        vi.useRealTimers()
        expect(page.state.entries.map(each => each.path)).toEqual([
          '.context/stories-story-map.md',
          '.context/stories-story-map.drawio',
          '.context/ddd-bounded-context.md',
          '.context/ddd-bounded-context.drawio',
        ])
      })
    })
  })
})

describe('Send Files App Failures To Chat', () => {
  describe('with files that do not list', () => {
    class FailingFilesServer extends FakeFilesServer {
      override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
        if (path.endsWith('/files')) throw new Error('cdd did not answer')
        return super.post<Result>(path, body)
      }
    }

    it('should send the failure to the chat that opened the page', async () => {
      const server = new FailingFilesServer()
      await started(new FilesPage(server, new FilesLink(STAGE_LINK)))
      const sent = server.posted('/send').map(post => [post.body.kind, JSON.parse(String(post.body.text)).failure])
      expect(sent).toEqual([['failure', 'The Files app did not list the files: cdd did not answer']])
    })
  })

  describe('with an open file that does not read', () => {
    class UnreadableFileServer extends FakeFilesServer {
      override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
        if (path.endsWith('/file')) throw new Error('the file is locked')
        return super.post<Result>(path, body)
      }
    }

    describe('that the person comes back to twice', () => {
      it('should send the failure to the chat once', async () => {
        const server = new UnreadableFileServer()
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        const stop = page.start()
        await settled()
        window.dispatchEvent(new Event('focus'))
        window.dispatchEvent(new Event('focus'))
        await settled()
        stop()
        expect(server.posted('/send').filter(post => post.body.kind === 'failure')).toHaveLength(1)
      })
    })
  })

  describe('with a failure nothing in the page caught', () => {
    it('should send it to the chat that opened the page', async () => {
      const server = new FakeFilesServer()
      const page = new FilesPage(server, new FilesLink(STAGE_LINK))
      const stop = page.start()
      await settled()
      window.dispatchEvent(new ErrorEvent('error', { error: new Error('a view broke') }))
      stop()
      const sent = server.posted('/send').map(post => JSON.parse(String(post.body.text)).failure)
      expect(sent).toEqual(['The Files page met a failure nothing caught: a view broke'])
    })
  })
})

describe('Browse Files Without Reading Rules', () => {
  describe('with a file open', () => {
    async function opened(): Promise<{ page: FilesPage; server: FakeFilesServer }> {
      const server = new FakeFilesServer()
      const page = new FilesPage(server, new FilesLink(`${STAGE_LINK}&file=.context/stories-story-map.md`))
      await started(page)
      return { page, server }
    }

    const lastRead = (server: FakeFilesServer) => server.posted('/file').at(-1)?.body

    it('should read it with no rules and no cross-file rules', async () => {
      const { server } = await opened()
      expect(lastRead(server)).toMatchObject({ rules: false, cross_file: false })
    })

    describe('that has Rules turned on', () => {
      it('should read it again with its rules', async () => {
        const { page, server } = await opened()
        await page.toggleRules()
        expect(lastRead(server)).toMatchObject({ rules: true, cross_file: false })
      })
    })

    describe('that has Cross-file turned on', () => {
      it('should read it again with only the rules across the whole working copy', async () => {
        const { page, server } = await opened()
        await page.toggleCrossFile()
        expect(lastRead(server)).toMatchObject({ rules: false, cross_file: true })
      })
    })
  })
})

describe('Filter Files By Format In Files App', () => {
  describe('with markdown and diagram files, no format chosen', () => {
    it('should show a chip for each format, none chosen', async () => {
      const page = new FilesPage(new FakeFilesServer(), new FilesLink(STAGE_LINK))
      await started(page)
      expect(page.state.formatChoices.map(chip => `${chip.label}:${chip.is_chosen}`)).toEqual(['markdown:false', 'diagram:false'])
    })

    describe('that has the diagram chip pressed', () => {
      async function pressedDiagram(): Promise<{ page: FilesPage; server: FakeFilesServer }> {
        const server = new FakeFilesServer()
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await started(page)
        await page.toggleFormat('diagram')
        return { page, server }
      }

      it('should choose the diagram format in the session, as the chat bar shows it', async () => {
        const { server } = await pressedDiagram()
        expect(server.posted('/choose-formats').map(post => post.body)).toEqual([{ fidelities: ['stories-story-map', 'ddd-bounded-context'], label: 'diagram', is_chosen: true }])
      })

      it('should list only the diagrams of the practice turned on', async () => {
        const { page } = await pressedDiagram()
        expect(page.state.entries.map(each => each.path)).toEqual(['.context/stories-story-map.drawio'])
      })

      it('should say why no file shows once the formats chosen hold none of them', async () => {
        const server = new FakeFilesServer()
        server.formats = [{ label: 'code', formats: ['python'], offered: 2, made: 0, is_chosen: true }]
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await started(page)
        expect(page.emptyReason).toBe('None of these files is in the formats chosen (</>): press a chosen format to show every format.')
      })

      it('should tell the chat bar to read its format chips again', async () => {
        const { server } = await pressedDiagram()
        expect(server.posted('/send').map(post => post.body)).toEqual([{ kind: 'refresh', text: 'formats' }])
      })
    })
  })
})

describe('Show Stages In Files App', () => {
  describe('with a ticket of two stages, the page opened on Discovery', () => {
    function twoStages(): FakeFilesServer {
      const server = new FakeFilesServer()
      server.practices.ddd = practice('ddd', 'DDD', '#2471a3', true)
      server.stages = { Discovery: ['stories-story-map', 'ddd-bounded-context'], Specification: ['stories-scenarios'] }
      return server
    }

    it("should show a button for each stage, Discovery's shown", async () => {
      const page = new FilesPage(twoStages(), new FilesLink(STAGE_LINK))
      await started(page)
      expect([Object.keys(page.state.stages), page.shownStageNames]).toEqual([['Discovery', 'Specification'], ['Discovery']])
    })

    describe('that has Specification turned on', () => {
      async function withSpecification(): Promise<{ page: FilesPage; server: FakeFilesServer }> {
        const server = twoStages()
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await started(page)
        await page.toggleStage('Specification')
        return { page, server }
      }

      it('should show both stages for the chat, as its chat bar shows them', async () => {
        const { server } = await withSpecification()
        expect(server.shownStages).toEqual(['Discovery', 'Specification'])
      })

      it('should list no file once both are turned off', async () => {
        const { page } = await withSpecification()
        await page.toggleStage('Discovery')
        await page.toggleStage('Specification')
        expect([page.shownStageNames, page.state.entries]).toEqual([[], []])
      })

      it("should list both stages' files", async () => {
        const { page } = await withSpecification()
        expect(page.state.entries.map(each => each.path)).toContain('.context/stories-scenarios.md')
      })
    })
  })
})
