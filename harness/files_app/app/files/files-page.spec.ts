// The Files app's acceptance tests for what only the page shows, story by story as
// story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md writes them; what the
// session answers is proved by story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review-files-in-files-app.story.domain.spec.py.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { GuidanceSelectionData } from '@cdd/space/session/session'

import { FilesLink } from './files-link'
import { FilesPage, filesShown, selectedFormatsOf } from './files-page'
import { drawioEditorUrl, drawioPageOf, missingNoteOf, revealLabelOf } from './files-paths'
import { calloutsOf, rulesOf } from './source-of-file'

// Each stage's fidelities by practice, as the session's practices declare them.
const FIDELITIES: Record<string, Record<string, string>> = {
  discovery: { stories: 'stories-story-map', ddd: 'ddd-bounded-context' },
  specification: { stories: 'stories-scenarios' },
}
const PRACTICES = [
  { key: 'stories', short_name: 'Stories', colour: '#c0392b' },
  { key: 'ddd', short_name: 'DDD', colour: '#2471a3' },
]

// The Files app's page against a fake of its own server: each post answers what the route would, and is kept in order.
// It holds the session's guidance selection as the session does, and answers a waiting read once the version passes it.
class FakeFilesServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = []
  version = 0
  stages: string[] | null = null
  practices = ['stories', 'ddd']
  formats: string[] = []
  rootFiles: object[] = []
  private readonly waiting: (() => void)[] = []

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    if (path.endsWith('/guidance-selection')) return this.selection() as Result
    if (path.endsWith('/show')) return { name: 'release-2', repo_name: 'abd-cdd', branch: 'release-2', root: 'C:/dev/abd-cdd-2' } as Result
    if (path.endsWith('/update-guidance-selection')) return this.update(body) as Result
    if (path.endsWith('/guidance-selection-after')) return (await this.after(Number(body.version))) as Result
    if (path.endsWith('/fidelity-files')) return Object.fromEntries((body.fidelities as string[]).map(slug => [slug, { markdown: [entry(`.context/${slug}.md`)], drawio: [entry(`.context/${slug}.drawio`)] }])) as Result
    if (path.endsWith('/root-files')) return this.rootFiles as Result
    return null
  }

  // A change made elsewhere, such as on the chat bar: the version moves and every waiting read answers.
  update(body: Record<string, unknown>): GuidanceSelectionData {
    if (body.stages) this.stages = [...(body.stages as string[])]
    if (body.practices) this.practices = [...(body.practices as string[])]
    if (body.formats) this.formats = [...(body.formats as string[])]
    this.version += 1
    this.waiting.splice(0).forEach(answer => answer())
    return this.selection()
  }

  private after(version: number): Promise<GuidanceSelectionData> {
    if (this.version > version) return Promise.resolve(this.selection())
    return new Promise(resolve => this.waiting.push(() => resolve(this.selection())))
  }

  selection(): GuidanceSelectionData {
    const chosen = this.stages ?? []
    const fidelities = this.listed()
    return {
      version: this.version,
      is_stage_chosen: this.stages !== null,
      stages: Object.keys(FIDELITIES).map(name => ({ name, title: name.charAt(0).toUpperCase() + name.slice(1), is_selected: chosen.includes(name) })),
      practices: PRACTICES.map(practice => ({ ...practice, is_selected: this.practices.includes(practice.key) })),
      formats: [
        { label: 'markdown', formats: ['markdown'], offered: fidelities.length, is_selected: this.formats.includes('markdown') },
        { label: 'diagram', formats: ['drawio', 'whiteboard'], offered: fidelities.length, is_selected: this.formats.includes('diagram') },
      ],
      fidelities,
    } as GuidanceSelectionData
  }

  // A filter with nothing selected filters nothing: no stage lists every stage, no practice every practice.
  private listed(): string[] {
    const stages = this.stages?.length ? this.stages : Object.keys(FIDELITIES)
    const practices = this.practices.length ? this.practices : PRACTICES.map(practice => practice.key)
    return stages.flatMap(stage => practices.map(key => FIDELITIES[stage]![key]).filter((slug): slug is string => Boolean(slug)))
  }

  posted(ending: string): { path: string; body: Record<string, unknown> }[] {
    return this.posts.filter(post => post.path.endsWith(ending))
  }
}

function entry(path: string) {
  return { path, exists: true, is_changed: false, link: '', format: '', fidelities: [] } as never
}

// The files under the session's root, as ticket.root_files answers them: two of the story map, a scenario of
// Specification, and two files no fidelity declares, the branch having changed story-flow.md and order.py.
const rootFile = (path: string, format: string, fidelities: string[], is_changed = false) => ({ path, exists: true, is_changed, link: '', format, fidelities })
const ROOT_FILES = [
  rootFile('.context/stories-story-map.md', 'markdown', ['stories-story-map']),
  rootFile('.context/story-flow.md', 'markdown', ['stories-story-map'], true),
  rootFile('specs/checkout.md', 'markdown', ['stories-scenarios']),
  rootFile('notes/plain.txt', '', []),
  rootFile('src/order.py', 'python', [], true),
]

const STAGE_LINK = '?files=release-2&fidelity=stories-story-map,ddd-bounded-context&chat=chat-1'

async function settled(): Promise<void> {
  for (let turn = 0; turn < 5; turn += 1) await new Promise(resolve => setTimeout(resolve, 0))
}

// The page as the person finds it once it opened: its files listed and the session's guidance selection read.
async function started(page: FilesPage): Promise<void> {
  page.start()()
  await settled()
}

// The page following the session's selection until stopped, as it does while it shows.
async function following(server: FakeFilesServer): Promise<{ page: FilesPage; stop: () => void }> {
  const page = new FilesPage(server, new FilesLink(STAGE_LINK))
  const stop = page.start()
  await settled()
  return { page, stop }
}

const paths = (page: FilesPage): string[] => page.state.entries.map(each => each.path)

describe('Select Guidance In Files App', () => {
  describe('with Discovery selected and both practices on', () => {
    function discovery(): FakeFilesServer {
      const server = new FakeFilesServer()
      server.stages = ['discovery']
      return server
    }

    it("should list both practices' Discovery files", async () => {
      const { page, stop } = await following(discovery())
      stop()
      expect(paths(page)).toEqual(['.context/stories-story-map.md', '.context/stories-story-map.drawio', '.context/ddd-bounded-context.md', '.context/ddd-bounded-context.drawio'])
    })

    describe('that has DDD turned off in the Files app', () => {
      it('should turn DDD off in the session', async () => {
        const server = discovery()
        const { page, stop } = await following(server)
        await page.guidance.togglePractice('ddd')
        stop()
        expect(server.posted('/update-guidance-selection').map(post => post.body.practices)).toEqual([['stories']])
      })

      it("should list only Stories' files", async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.togglePractice('ddd')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.md', '.context/stories-story-map.drawio'])
      })
    })

    describe('that has Specification selected in the Files app', () => {
      it("should list both stages' files, reading Specification's the first time it shows", async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.toggleStage('specification')
        await settled()
        stop()
        expect(paths(page)).toContain('.context/stories-scenarios.md')
      })
    })

    describe('that has the diagram format selected in the Files app', () => {
      it('should list only the diagrams', async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.toggleFormat('diagram')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.drawio', '.context/ddd-bounded-context.drawio'])
      })
    })

    describe('that has every stage turned off', () => {
      it('should list the files of every stage, as no stage filter', async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.toggleStage('discovery')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.md', '.context/stories-story-map.drawio', '.context/ddd-bounded-context.md', '.context/ddd-bounded-context.drawio', '.context/stories-scenarios.md', '.context/stories-scenarios.drawio'])
      })
    })

    describe('that has the chat bar turn DDD off', () => {
      it('should draw it off without a press here', async () => {
        const server = discovery()
        const { page, stop } = await following(server)
        server.update({ practices: ['stories'] })
        await settled()
        stop()
        expect(page.state.guidance?.practices.map(practice => `${practice.key}:${practice.is_selected}`)).toEqual(['stories:true', 'ddd:false'])
      })
    })

    describe('that has a press answered before an older read', () => {
      it('should keep the press drawn', async () => {
        const server = discovery()
        const { page, stop } = await following(server)
        await page.guidance.togglePractice('ddd')
        await (page as unknown as { guidance: { accept(answer: GuidanceSelectionData): Promise<void> } }).guidance.accept({ ...server.selection(), version: 0, practices: [] })
        stop()
        expect(page.state.guidance?.version).toBe(1)
      })
    })
  })

  describe('with no stage chosen yet', () => {
    it('should list the files of the fidelities its link names', async () => {
      const { page, stop } = await following(new FakeFilesServer())
      stop()
      expect(paths(page)).toEqual(['.context/stories-story-map.md', '.context/stories-story-map.drawio', '.context/ddd-bounded-context.md', '.context/ddd-bounded-context.drawio'])
    })

    describe('that has DDD turned off in the Files app', () => {
      it("should list only Stories' files among those its link names", async () => {
        const { page, stop } = await following(new FakeFilesServer())
        await page.guidance.togglePractice('ddd')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.md', '.context/stories-story-map.drawio'])
      })
    })
  })
})

describe('Head The Files App With Where The Files Are', () => {
  it('should name the repository, the branch, and the session root', async () => {
    const { page, stop } = await following(new FakeFilesServer())
    stop()
    expect(page.heading).toBe('abd-cdd · release-2 · C:/dev/abd-cdd-2')
  })

  describe('with a link that names no session', () => {
    async function opened(): Promise<{ page: FilesPage; server: FakeFilesServer }> {
      const server = new FakeFilesServer()
      const page = new FilesPage(server, new FilesLink(''))
      page.start()()
      await settled()
      return { page, server }
    }

    it('should ask cdd about no session', async () => {
      const { server } = await opened()
      expect(server.posts.filter(post => post.path.startsWith('/session/'))).toEqual([])
    })

    it('should say to open it from the chat bar', async () => {
      const { page } = await opened()
      expect(page.state.problem).toBe('This link names no files: open the Files app from the chat bar.')
    })
  })
})

describe('Review All Session Files Or This Session', () => {
  async function discovery(formats: string[] = [], practices = ['stories', 'ddd']): Promise<FilesPage> {
    const server = new FakeFilesServer()
    server.stages = ['discovery']
    server.formats = formats
    server.practices = practices
    server.rootFiles = ROOT_FILES
    const { page, stop } = await following(server)
    stop()
    return page
  }

  describe('that has All session files pressed', () => {
    it('should list every file under the root of the stages and practices selected', async () => {
      const page = await discovery()
      page.showScope('all')
      expect(page.fileBar.entries.map(each => each.path)).toEqual(expect.arrayContaining(['.context/stories-story-map.md', '.context/story-flow.md']))
    })

    it('should leave out a file of a stage not selected', async () => {
      const page = await discovery()
      page.showScope('all')
      expect(page.fileBar.entries.map(each => each.path)).not.toContain('specs/checkout.md')
    })

    it('should leave out a file of no fidelity while a practice is selected', async () => {
      const page = await discovery()
      page.showScope('all')
      expect(page.fileBar.entries.map(each => each.path)).not.toContain('notes/plain.txt')
    })

    describe('with no practice selected', () => {
      it('should list the files of every practice and of no fidelity', async () => {
        const page = await discovery([], [])
        page.showScope('all')
        expect(page.fileBar.entries.map(each => each.path)).toEqual(expect.arrayContaining(['.context/stories-story-map.md', '.context/ddd-bounded-context.md', 'notes/plain.txt', 'src/order.py']))
      })
    })

    it('should list only the files in the formats selected', async () => {
      const page = await discovery(['markdown'])
      page.showScope('all')
      expect(page.fileBar.entries.map(each => each.path)).toEqual(['.context/stories-story-map.md', '.context/ddd-bounded-context.md', '.context/story-flow.md'])
    })
  })

  describe('that lists This session, its default', () => {
    it('should list only the files the branch changed', async () => {
      const page = await discovery()
      expect(page.fileBar.entries.map(each => each.path)).toEqual(['.context/story-flow.md'])
    })
  })

  describe('with a file renamed on disk since the page listed it', () => {
    async function renamed(): Promise<FilesPage> {
      const server = new FakeFilesServer()
      server.practices = []
      server.rootFiles = ROOT_FILES
      const { page, stop } = await following(server)
      stop()
      server.rootFiles = ROOT_FILES.map(file => (file.path === 'src/order.py' ? { ...file, path: 'src/basket.py' } : file))
      return page
    }

    describe('that has All session files pressed again', () => {
      it('should list the file under its new name', async () => {
        const page = await renamed()
        page.showScope('all')
        await settled()
        expect(page.fileBar.entries.map(each => each.path)).toContain('src/basket.py')
      })

      it('should list its old name no longer', async () => {
        const page = await renamed()
        page.showScope('all')
        await settled()
        expect(page.fileBar.entries.map(each => each.path)).not.toContain('src/order.py')
      })
    })
  })
})

describe('Filter Files By Format In Files App', () => {
  it('should say why no file shows once the formats selected hold none of them', async () => {
    const server = new FakeFilesServer()
    server.stages = ['discovery']
    server.formats = ['diagram']
    const page = new FilesPage(server, new FilesLink(STAGE_LINK))
    await started(page)
    page.store.change(state => ({ byFidelity: state.byFidelity.map(each => ({ ...each, formatOf: {} })) }))
    expect(page.emptyReason).toBe('None of these files is in the formats chosen (◇): press a chosen format to show every format.')
  })

  it('should show every file of the fidelities listed while no format is selected', () => {
    const shown = filesShown([{ slug: 'stories-story-map', entries: [entry('.context/story-map.md')] }], ['stories-story-map'])
    expect(shown.map(each => each.path)).toEqual(['.context/story-map.md'])
  })

  // A board published from the story map opens in Claude, so it shows whatever formats are chosen; requested
  // 2026-11-18: "first of all where is whiteboard link" while only markdown and drawio were chosen.
  it('should show a published whiteboard while only other formats are selected', () => {
    const board = { ...(entry('.context/story-map.version-2.whiteboard') as object), link: 'https://claude.ai/artifact/board' } as never
    const files = [{ slug: 'stories-story-map', entries: [entry('.context/story-map.md'), board], formatOf: { '.context/story-map.md': 'markdown', '.context/story-map.version-2.whiteboard': 'whiteboard' } }]
    const shown = filesShown(files, ['stories-story-map'], ['markdown', 'drawio'])
    expect(shown.map(each => each.path)).toEqual(['.context/story-map.md', '.context/story-map.version-2.whiteboard'])
  })

  // A diagram is a draw.io file and a Claude Whiteboard board, so the diagram filter shows a board not yet published
  // too; requested 2026-11-20: "whiteboard isn't a separate format, there's only a button for 'diagram'".
  it('should show the whiteboard beside the draw.io file while the diagram is selected', () => {
    const server = new FakeFilesServer()
    server.formats = ['diagram']
    const files = [{ slug: 'stories-story-map', entries: [entry('.context/story-map.md'), entry('.context/story-map.drawio'), entry('.context/story-map.whiteboard')], formatOf: { '.context/story-map.md': 'markdown', '.context/story-map.drawio': 'drawio', '.context/story-map.whiteboard': 'whiteboard' } }]
    const shown = filesShown(files, ['stories-story-map'], selectedFormatsOf(server.selection()))
    expect(shown.map(each => each.path)).toEqual(['.context/story-map.drawio', '.context/story-map.whiteboard'])
  })
})

describe('Open Diagram In Files App', () => {
  describe('with a .drawio file listed', () => {
    it("should show it at the Files server's draw.io page, which starts the viewer on it", () => {
      expect(drawioPageOf('C:/dev/work/.context/a.drawio', 'chat-1')).toBe('/api/drawio/page?path=C%3A%2Fdev%2Fwork%2F.context%2Fa.drawio&chat=chat-1')
    })

    it("should name the page's project, so the viewer opens that project's file whichever project started it", () => {
      expect(drawioPageOf('src/.context/a.drawio', 'chat-1', 'C:/dev/shop')).toBe('/api/drawio/page?path=src%2F.context%2Fa.drawio&chat=chat-1&project=C%3A%2Fdev%2Fshop')
    })

    it('should take the project its link names', () => {
      expect(new FilesLink('?project=C%3A%2Fdev%2Fshop&files=main').project).toBe('C:/dev/shop')
    })

    it("should open the viewer on the file's whole path in the page's project", () => {
      expect(drawioEditorUrl('src/.context/a.drawio', 'C:\\dev\\shop\\')).toBe(`http://127.0.0.1:8791/edit?f=${encodeURIComponent('C:\\dev\\shop/src/.context/a.drawio')}`)
    })

    it('should open the viewer on the port it answers on, when that is not its usual one', () => {
      expect(drawioEditorUrl('src/a.drawio', 'C:/dev/shop', 9123)).toBe(`http://127.0.0.1:9123/edit?f=${encodeURIComponent('C:/dev/shop/src/a.drawio')}`)
    })

    it('should leave a whole path, or a path with no project, as it is', () => {
      expect(drawioEditorUrl('C:/dev/work/a.drawio', 'C:/dev/shop')).toBe(`http://127.0.0.1:8791/edit?f=${encodeURIComponent('C:/dev/work/a.drawio')}`)
      expect(drawioEditorUrl('src/a.drawio', '')).toBe(`http://127.0.0.1:8791/edit?f=${encodeURIComponent('src/a.drawio')}`)
    })

    describe('that the Person opens', () => {
      async function opened() {
        const server = new FakeFilesServer()
        const page = new FilesPage(server, new FilesLink(STAGE_LINK))
        await started(page)
        const read = server.posted('/file').length
        await page.open('.context/stories-story-map.drawio')
        return { page, server, read }
      }

      it('should show it in the file view, beside the file list', async () => {
        expect((await opened()).page.state.openPath).toBe('.context/stories-story-map.drawio')
      })

      it('should ask the session for no text of it, as the draw.io editor reads it', async () => {
        const { server, read } = await opened()
        expect(server.posted('/file').length).toBe(read)
      })
    })
  })
})

describe('Open File In File Browser', () => {
  describe('with a file listed', () => {
    async function rightClicked(server = new FakeFilesServer()) {
      const page = new FilesPage(server, new FilesLink(STAGE_LINK))
      await started(page)
      page.menu.open('.context/stories-story-map.md', 40, 80)
      return { page, server }
    }

    describe('that the Person right-clicks', () => {
      it('should show its menu where the Person clicked', async () => {
        expect((await rightClicked()).page.state.menu).toEqual({ path: '.context/stories-story-map.md', x: 40, y: 80 })
      })

      describe('and opens in the file browser', () => {
        async function revealed(server = new FakeFilesServer()) {
          const opened = await rightClicked(server)
          await opened.page.menu.reveal()
          return opened
        }

        it("should ask the Files server to show it in the system's file browser", async () => {
          const { server } = await revealed()
          expect(server.posted('/reveal').map(post => post.body.path)).toEqual(['.context/stories-story-map.md'])
        })

        it('should close the menu', async () => {
          expect((await revealed()).page.state.menu).toBeNull()
        })

        describe('with a file browser that does not open', () => {
          class RefusingFilesServer extends FakeFilesServer {
            override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
              if (path.endsWith('/reveal')) throw new Error('explorer.exe is not there')
              return super.post<Result>(path, body)
            }
          }

          it('should tell the chat that opened the page', async () => {
            const { server } = await revealed(new RefusingFilesServer())
            const sent = server.posted('/send').map(post => JSON.parse(String(post.body.text)).failure)
            expect(sent).toContain('.context/stories-story-map.md did not open in the file browser: explorer.exe is not there')
          })
        })
      })

      describe('and presses elsewhere', () => {
        it('should close the menu', async () => {
          const { page } = await rightClicked()
          page.menu.close()
          expect(page.state.menu).toBeNull()
        })
      })
    })
  })

  it("should name the menu's choice for the system the page runs on", () => {
    expect(['Win32', 'MacIntel', 'Linux x86_64'].map(revealLabelOf)).toEqual(['Open in Explorer', 'Reveal in Finder', 'Open in file manager'])
  })
})

describe('Name A File The List Cannot Open', () => {
  it('should say a file the branch deleted is deleted on this branch, and one not there yet is not generated yet', () => {
    const missing = (is_changed: boolean) => ({ path: 'harness/process/git.py', exists: false, is_changed, link: '', format: 'python', fidelities: [] })
    expect([missingNoteOf(missing(true)), missingNoteOf(missing(false))]).toEqual(['deleted on this branch', 'not generated yet'])
  })
})

describe('Add File Or Selection To Chat Context', () => {
  async function opened(server = new FakeFilesServer()) {
    const page = new FilesPage(server, new FilesLink(STAGE_LINK))
    await started(page)
    return { page, server }
  }

  const addedBodies = (server: FakeFilesServer) => server.posted('/add-to-chat-context').map(post => post.body)

  describe('with a file listed', () => {
    describe("that the Person adds to the chat's context from its menu", () => {
      async function added(server = new FakeFilesServer()) {
        const done = await opened(server)
        done.page.menu.open('src/checkout/order.py', 40, 80)
        await done.page.menu.addToContext()
        return done
      }

      it('should ask the session to add the whole file to the chat that opened the page', async () => {
        expect(addedBodies((await added()).server)).toEqual([{ chat: 'chat-1', path: 'src/checkout/order.py' }])
      })

      it('should close the menu', async () => {
        expect((await added()).page.state.menu).toBeNull()
      })

      it('should say so in a toast', async () => {
        expect((await added()).page.state.toasts).toContain("order.py added to the chat's context")
      })

      describe('with a chat that is not connected', () => {
        class NotConnectedServer extends FakeFilesServer {
          override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
            if (path.endsWith('/add-to-chat-context')) throw new Error("chat 'chat-1' is not connected: is the cdd-board mod loaded in it?")
            return super.post<Result>(path, body)
          }
        }

        it('should say so in a toast', async () => {
          const { page } = await added(new NotConnectedServer())
          expect(page.state.toasts).toContain("order.py was not added to the chat's context: chat 'chat-1' is not connected: is the cdd-board mod loaded in it?")
        })
      })
    })
  })

  describe('with lines 12 to 14 of the open file selected', () => {
    describe("that the Person adds to the chat's context", () => {
      it('should ask the session to add those lines to the chat that opened the page', async () => {
        const { page, server } = await opened()
        await page.chatContext.add('src/checkout/order.py', { start: 12, end: 14 })
        expect(addedBodies(server)).toEqual([{ chat: 'chat-1', path: 'src/checkout/order.py', start_line: 12, end_line: 14 }])
      })
    })
  })
})

// A whiteboard opens in Claude Desktop's artifact panel, beside the chat, not in a browser: the page asks the chat that
// opened it to open the board; requested 2026-11-18: "im in claude desktop i want it open in desktop".
describe('Open Whiteboard In Claude Desktop', () => {
  const board = { path: '.context/story-map.version-2.whiteboard', exists: true, is_changed: true, link: 'https://claude.ai/artifact/board-2', format: 'whiteboard', fidelities: [] } as never

  it('should ask the chat that opened the page to open the board in its artifact panel', async () => {
    const server = new FakeFilesServer()
    const page = new FilesPage(server, new FilesLink(STAGE_LINK))
    await started(page)
    await page.openPublished(board)
    const asked = server.posted('/send').filter(post => post.body.kind === 'submit').map(post => String(post.body.text))
    expect(asked).toHaveLength(1)
    expect(asked[0]).toContain('https://claude.ai/artifact/board-2')
  })

  it('should say the page cannot reach a chat when none opened it', async () => {
    const server = new FakeFilesServer()
    const page = new FilesPage(server, new FilesLink(STAGE_LINK.replace('&chat=chat-1', '')))
    await started(page)
    expect(await page.openPublished(board)).toBe(false)
    expect(server.posted('/send').filter(post => post.body.kind === 'submit')).toHaveLength(0)
  })
})

// Correct on a broken rule's banner reaches the chat the way a comment does: a comment on the rule's lines, saying what
// to fix, sent to the chat that opened the page; requested 2026-11-20: Correct must work "the same as comments".
describe('Correct Broken Rule As A Comment', () => {
  const CORRECTION = {
    rule: 'limit-operation-parameters',
    message: "Operation 'place' takes 4 parameters (maximum 2).",
    nodeName: 'order.py',
    nodeType: 'File',
    file: 'src/order.py',
    startLine: 2,
    endLine: 3,
    excerpt: 'class Order:\n    def place(self, cart, user, store, day):\n        return self',
  }

  // A session with src/order.py open, which keeps each comment added and answers it sent once sent, as file-comments does.
  class CommentingServer extends FakeFilesServer {
    comments: { anchor: string; range: object; text: string; state: string }[] = []
    isChatDown = false

    override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
      if (path.endsWith('/file')) return { path: 'src/order.py', text: CORRECTION.excerpt, language: 'python', comments: this.comments, changes: [], folds: [] } as Result
      if (!path.includes('/file-comments/')) return super.post<Result>(path, body)
      this.posts.push({ path, body })
      if (path.endsWith('/add')) this.comments.push({ anchor: `${body.path}:L${body.start_line}-L${body.end_line}`, range: {}, text: String(body.text), state: 'not_sent' })
      if (path.endsWith('/send') && this.isChatDown) throw new Error("chat 'chat-1' is not connected: is the cdd-board mod loaded in it?")
      if (path.endsWith('/send')) this.comments = this.comments.map(comment => (comment.anchor === body.anchor ? { ...comment, state: 'sent' } : comment))
      return { session_file: 'release-2', comments: this.comments } as Result
    }
  }

  async function corrected(server = new CommentingServer(), link = STAGE_LINK) {
    const page = new FilesPage(server, new FilesLink(`${link}&file=src/order.py`))
    await started(page)
    const outcome = await page.comments.correct(CORRECTION)
    return { page, server, outcome }
  }

  const commentPosts = (server: FakeFilesServer, ending: string) => server.posts.filter(post => post.path.includes('/file-comments/') && post.path.endsWith(ending)).map(post => post.body)

  describe('with the chat that opened the page connected', () => {
    it("should comment on the rule's lines of the open file", async () => {
      const { server } = await corrected()
      expect(commentPosts(server, '/add')).toEqual([expect.objectContaining({ path: 'src/order.py', start_line: 2, end_line: 3 })])
    })

    it('should say in the comment which rule is broken, what is wrong, and to fix it test first', async () => {
      const text = String(commentPosts((await corrected()).server, '/add')[0]?.text)
      expect(text).toContain('Rule: limit-operation-parameters')
      expect(text).toContain("Violation: Operation 'place' takes 4 parameters (maximum 2).")
      expect(text).toContain('test-driven')
    })

    it('should leave the lines out of the comment, since a sent comment quotes them', async () => {
      expect(String(commentPosts((await corrected()).server, '/add')[0]?.text)).not.toContain('def place')
    })

    it('should send the comment to the chat that opened the page', async () => {
      expect(commentPosts((await corrected()).server, '/send')).toEqual([{ anchor: 'src/order.py:L2-L3', chat: 'chat-1' }])
    })

    it('should answer that it was sent to the chat', async () => {
      expect((await corrected()).outcome).toEqual({ isSent: true, words: 'Sent to chat' })
    })
  })

  describe('with a chat that is not connected', () => {
    it('should answer that it was not sent', async () => {
      const server = new CommentingServer()
      server.isChatDown = true
      expect((await corrected(server)).outcome).toEqual({ isSent: false, words: 'Not sent' })
    })

    it('should say why in a toast', async () => {
      const server = new CommentingServer()
      server.isChatDown = true
      expect((await corrected(server)).page.state.toasts).toContain("The comment src/order.py:L2-L3 was not sent: chat 'chat-1' is not connected: is the cdd-board mod loaded in it?")
    })
  })

  describe('with no chat that opened the page', () => {
    it('should answer that it was not sent', async () => {
      expect((await corrected(new CommentingServer(), STAGE_LINK.replace('&chat=chat-1', ''))).outcome).toEqual({ isSent: false, words: 'Not sent' })
    })
  })
})

describe('Send Files App Failures To Chat', () => {
  describe('with files that do not list', () => {
    class FailingFilesServer extends FakeFilesServer {
      override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
        if (path.endsWith('/fidelity-files')) throw new Error('cdd did not answer')
        return super.post<Result>(path, body)
      }
    }

    it('should send the failure to the chat that opened the page', async () => {
      const server = new FailingFilesServer()
      await started(new FilesPage(server, new FilesLink(STAGE_LINK)))
      const sent = server.posted('/send').map(post => [post.body.kind, JSON.parse(String(post.body.text)).failure])
      expect(sent).toContainEqual(['failure', 'The Files app did not list the files: cdd did not answer'])
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

describe('View File In Source View', () => {
  // A cdd server lane older than the page, such as the pinned stable lane: its session.file answers what it knew then.
  class OlderLaneFilesServer extends FakeFilesServer {
    constructor(private readonly answer: unknown) {
      super()
    }

    override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
      if (path.endsWith('/file')) return this.answer as Result
      return super.post<Result>(path, body)
    }
  }

  async function viewed(answer: unknown) {
    const server = new OlderLaneFilesServer(answer)
    const page = new FilesPage(server, new FilesLink(STAGE_LINK))
    await started(page)
    await page.open('src/order.py')
    return { page, server }
  }

  const ORDER_PY = { path: 'src/order.py', text: 'class Order:\n    def place(self, cart: Cart) -> Order:\n        return self', language: 'python', comments: [], changes: [], folds: [] }

  describe('with a server lane that answers order.py without callouts, steps or violations', () => {
    it('should show order.py with no callout', async () => {
      const { page } = await viewed(ORDER_PY)
      expect(calloutsOf(page.state.file!)).toEqual([])
    })

    it('should show order.py with no broken rule', async () => {
      const { page } = await viewed(ORDER_PY)
      expect(rulesOf(page.state.file!)).toEqual([])
    })

    it('should say nothing went wrong', async () => {
      expect((await viewed(ORDER_PY)).page.state.problem).toBe('')
    })
  })

  describe('with a server lane that answers a step without what it invokes or observes', () => {
    it('should put no callout on the step', async () => {
      const { page } = await viewed({ ...ORDER_PY, steps: [{ line: 2 }] })
      expect(calloutsOf(page.state.file!)).toEqual([])
    })
  })

  describe('with a server lane that answers no file, such as the text of a call it cannot run', () => {
    it('should show that order.py did not open', async () => {
      const { page } = await viewed('Unknown tool: session.file')
      expect(page.state.problem).toBe('src/order.py did not open: session.file answered no file: Unknown tool: session.file')
    })

    it('should hold no file to draw', async () => {
      expect((await viewed('Unknown tool: session.file')).page.state.file).toBeNull()
    })
  })
})
