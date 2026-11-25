// The Files app's acceptance tests for what only the page shows, story by story as
// story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md writes them; what the
// session answers is proved by story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review-files-in-files-app.story.domain.spec.py.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { GuidanceSelectionData } from '@cdd/space/session/session'

import { FilesLink } from './files-link'
import { FilesPage } from './files-page'
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
    if (path.endsWith('/toggle-guidance')) return this.toggle(String(body.part), String(body.name)) as Result
    if (path.endsWith('/guidance-selection-after')) return (await this.after(Number(body.version))) as Result
    if (path.endsWith('/fidelity-files')) return this.fidelityFiles(body.fidelities as string[], (body.linked as string[] | null) ?? (body.fidelities as string[])) as Result
    if (path.endsWith('/root-files')) return this.rootFilesFor((body.linked as string[] | null) ?? []) as Result
    return null
  }

  // Each fidelity's markdown and drawio file, as ticket.fidelity_files answers them for the selection and the fidelities
  // the link names: listed while the fidelity is listed and its format selected, or none is; a file of a fidelity listed
  // that the formats selected leave out names them.
  private fidelityFiles(slugs: string[], linked: string[]) {
    const listed = this.listedFor(linked)
    const formats = this.formatsSelected()
    const inFormats = (format: string) => !formats.length || formats.includes(format)
    const answered = (slug: string, format: string, path: string) => ({
      ...(entry(path) as object),
      is_listed: listed.includes(slug) && inFormats(format),
      is_session_work: false,
      hidden_by_formats: listed.includes(slug) && !inFormats(format) ? this.labelsSelected() : [],
    })
    return Object.fromEntries(slugs.map(slug => [slug, { markdown: [answered(slug, 'markdown', `.context/${slug}.md`)], drawio: [answered(slug, 'drawio', `.context/${slug}.drawio`)] }]))
  }

  // The files under the root, as ticket.root_files answers them: listed while in a format selected, or none is, and of a
  // fidelity listed; a file of no fidelity only while no practice is selected. The session's own work is what the
  // branch changed.
  private rootFilesFor(linked: string[]) {
    const listed = this.listedFor(linked)
    const formats = this.formatsSelected()
    return (this.rootFiles as { format: string; fidelities: string[]; is_changed: boolean }[]).map(file => {
      const inFormats = !formats.length || formats.includes(file.format)
      const belongs = file.fidelities.length ? file.fidelities.some(slug => listed.includes(slug)) : !this.practices.length
      return { ...file, is_listed: inFormats && belongs, is_session_work: file.is_changed, hidden_by_formats: belongs && !inFormats ? this.labelsSelected() : [] }
    })
  }

  // The fidelities whose files are listed: those the selection covers once stages were chosen, else those the link names
  // that it covers.
  private listedFor(linked: string[]): string[] {
    const covered = this.listed()
    return this.stages !== null ? covered : linked.filter(slug => covered.includes(slug))
  }

  private labelsSelected(): string[] {
    return this.selection().formats.filter(format => format.is_selected).map(format => format.label)
  }

  private formatsSelected(): string[] {
    return this.selection().formats.filter(format => format.is_selected).flatMap(format => format.formats)
  }

  // A press, as Session.toggle_guidance answers it: the one named taken out of those selected, or put in.
  toggle(part: string, name: string): GuidanceSelectionData {
    const flip = (names: string[]) => (names.includes(name) ? names.filter(each => each !== name) : [...names, name])
    if (part === 'stage') return this.update({ stages: flip(this.stages ?? []) })
    if (part === 'practice') return this.update({ practices: flip(this.practices) })
    return this.update({ formats: flip(this.formats) })
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
      covered_stages: (chosen.length ? chosen : Object.keys(FIDELITIES)).map(name => name.charAt(0).toUpperCase() + name.slice(1)),
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
        await page.guidance.toggle('practice', 'ddd')
        stop()
        expect(server.posted('/toggle-guidance').map(post => post.body)).toEqual([{ part: 'practice', name: 'ddd' }])
      })

      it("should list only Stories' files", async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.toggle('practice', 'ddd')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.md', '.context/stories-story-map.drawio'])
      })
    })

    describe('that has Specification selected in the Files app', () => {
      it("should list both stages' files, reading Specification's the first time it shows", async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.toggle('stage', 'specification')
        await settled()
        stop()
        expect(paths(page)).toContain('.context/stories-scenarios.md')
      })
    })

    describe('that has the diagram format selected in the Files app', () => {
      it('should list only the diagrams', async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.toggle('format', 'diagram')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.drawio', '.context/ddd-bounded-context.drawio'])
      })
    })

    describe('that has every stage turned off', () => {
      it('should list the files of every stage, as no stage filter', async () => {
        const { page, stop } = await following(discovery())
        await page.guidance.toggle('stage', 'discovery')
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
        await page.guidance.toggle('practice', 'ddd')
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
        await page.guidance.toggle('practice', 'ddd')
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
    expect(page.emptyReason).toBe('None of these files is in the formats chosen (◇): press a chosen format to show every format.')
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

// Open Whiteboard In Files App: a whiteboard file opens as the board Python reads from it (whiteboard-file.show), which the
// canvas draws; the page never reads the file's text to draw it.
describe('Open Whiteboard In Files App', () => {
  const WHITEBOARD = '.context/story-map.whiteboard'
  const BOARD = { title: 'Story Map', sections: [], shapes: [], labels: [], arrows: [] }

  // A session whose whiteboard file holds BOARD, or holds no board at all.
  class BoardServer extends FakeFilesServer {
    isUnreadable = false

    override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
      if (!path.startsWith('/whiteboard-file/')) return super.post<Result>(path, body)
      this.posts.push({ path, body })
      if (this.isUnreadable) throw new Error('cdd whiteboard-file.show failed: UnreadableBoard: Not a whiteboard file')
      return { path: decodeURIComponent(path.split('/')[2] ?? ''), board: BOARD } as Result
    }
  }

  const opened = async (server: BoardServer): Promise<FilesPage> => {
    const page = new FilesPage(server, new FilesLink(`${STAGE_LINK}&file=${encodeURIComponent(WHITEBOARD)}`))
    await started(page)
    return page
  }

  it('should read the board through whiteboard-file.show', async () => {
    const server = new BoardServer()
    await opened(server)
    expect(server.posts.filter(post => post.path.startsWith('/whiteboard-file/')).map(post => post.path)).toEqual([`/whiteboard-file/${encodeURIComponent(WHITEBOARD)}/show`])
  })

  it('should hold the board it answered, for the canvas to draw', async () => {
    expect((await opened(new BoardServer())).state.board).toEqual(BOARD)
  })

  it('should not read the file\'s text through session.file', async () => {
    const server = new BoardServer()
    await opened(server)
    expect(server.posted('/file')).toHaveLength(0)
  })

  it('should say the file did not open when it holds no board', async () => {
    const server = new BoardServer()
    server.isUnreadable = true
    expect((await opened(server)).state.problem).toContain('Not a whiteboard file')
  })
})

// A whiteboard opens in Claude Desktop's artifact panel, beside the chat, not in a browser: the page asks the chat that
// opened it to open the board; requested 2026-11-18: "im in claude desktop i want it open in desktop".
describe('Open Whiteboard In Claude Desktop', () => {
  const board = { path: '.context/story-map.version-2.whiteboard', exists: true, is_changed: true, link: 'https://claude.ai/artifact/board-2', published_kind: 'whiteboard', format: 'whiteboard', fidelities: [] } as never

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

  // Pressing a whiteboard that is on a board opens that board in Claude, never a drawing of the file beside the list;
  // requested 2026-11-25: the file list must link to the Claude whiteboard.
  it('should open the board in Claude when a whiteboard on a board is pressed', async () => {
    const server = new FakeFilesServer()
    const page = new FilesPage(server, new FilesLink(STAGE_LINK))
    await started(page)
    await page.press(board)
    const asked = server.posted('/send').filter(post => post.body.kind === 'submit').map(post => String(post.body.text))
    expect(asked).toHaveLength(1)
    expect(asked[0]).toContain('https://claude.ai/artifact/board-2')
  })

  it('should not draw the file beside the list when a whiteboard on a board is pressed', async () => {
    const server = new FakeFilesServer()
    const page = new FilesPage(server, new FilesLink(STAGE_LINK))
    await started(page)
    await page.press(board)
    expect(page.state.openPath).not.toBe('.context/story-map.version-2.whiteboard')
  })
})

// Fix this one on a broken rule's banner reaches the chat the way a comment does: a comment on the place's lines,
// saying what to fix, sent to the chat that opened the page; requested 2026-11-20: Correct, now Fix this one, must work
// "the same as comments". Fix rule and Fix all ask Python to comment on each place and send them together.
describe('Fix Broken Rule As A Comment', () => {
  // The words Python writes beside the file's violation; Python's spec pins them.
  const COMMENT = "Fix this violation using the Clean Engineering practice guidelines and a test-driven approach.\n…\nRule: limit-operation-parameters\nViolation: Operation 'place' takes 4 parameters (maximum 2)."
  const ORDER = 'class Order:\n    def place(self, cart, user, store, day):\n        return self'
  const CORRECTION = {
    rule: 'limit-operation-parameters',
    place: { message: "Operation 'place' takes 4 parameters (maximum 2).", startLine: 2, endLine: 3, correctionComment: COMMENT },
    nodeId: '',
    startLine: 2,
    endLine: 3,
  }

  // A session with src/order.py open, which keeps each comment added and answers it sent once sent, as file-comments does.
  class CommentingServer extends FakeFilesServer {
    comments: { anchor: string; range: object; text: string; state: string }[] = []
    isChatDown = false

    override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
      if (path.endsWith('/file')) return { path: 'src/order.py', text: ORDER, language: 'python', comments: this.comments, changes: [], folds: [] } as Result
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
    const outcome = await page.comments.fixOne(CORRECTION)
    return { page, server, outcome }
  }

  const commentPosts = (server: FakeFilesServer, ending: string) => server.posts.filter(post => post.path.includes('/file-comments/') && post.path.endsWith(ending)).map(post => post.body)

  describe('with the chat that opened the page connected', () => {
    it("should comment on the rule's lines of the open file", async () => {
      const { server } = await corrected()
      expect(commentPosts(server, '/add')).toEqual([expect.objectContaining({ path: 'src/order.py', start_line: 2, end_line: 3 })])
    })

    it('should comment in the words Python wrote beside the violation', async () => {
      expect(commentPosts((await corrected()).server, '/add')[0]?.text).toEqual(COMMENT)
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

  async function fixed(fix: (page: FilesPage) => Promise<unknown>, link = STAGE_LINK) {
    const server = new CommentingServer()
    const page = new FilesPage(server, new FilesLink(`${link}&file=src/order.py`))
    await started(page)
    const outcome = await fix(page)
    return { page, server, outcome }
  }

  describe('fixed by the rule', () => {
    it('should ask Python to comment on every place of the rule in the open file and send them to the chat that opened the page', async () => {
      const { server } = await fixed(page => page.comments.fixRule('limit-operation-parameters'))
      expect(commentPosts(server, '/fix')).toEqual([{ path: 'src/order.py', chat: 'chat-1', rule: 'limit-operation-parameters', cross_file: false }])
    })

    it('should answer that it was sent to the chat', async () => {
      expect((await fixed(page => page.comments.fixRule('limit-operation-parameters'))).outcome).toEqual({ isSent: true, words: 'Sent to chat' })
    })
  })

  describe('fixed all at once', () => {
    it('should ask Python to comment on every broken place in the open file, of any rule', async () => {
      const { server } = await fixed(page => page.comments.fixAll())
      expect(commentPosts(server, '/fix')).toEqual([{ path: 'src/order.py', chat: 'chat-1', rule: '', cross_file: false }])
    })

    describe('with no chat that opened the page', () => {
      it('should send nothing and answer that it was not sent', async () => {
        const { server, outcome } = await fixed(page => page.comments.fixAll(), STAGE_LINK.replace('&chat=chat-1', ''))
        expect([commentPosts(server, '/fix'), outcome]).toEqual([[], { isSent: false, words: 'Not sent' }])
      })
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

// Which callouts a file holds is the session's answer for the file view's filters (session.file paths and node_filter):
// the page sends them with each read and reads its open files again when one changes.
describe("Show The Callouts The File View's Filters Select", () => {
  const lastRead = (server: FakeFilesServer) => server.posted('/file').at(-1)?.body

  async function opened(): Promise<{ page: FilesPage; server: FakeFilesServer; stop: () => void }> {
    const server = new FakeFilesServer()
    server.rootFiles = ROOT_FILES
    const page = new FilesPage(server, new FilesLink(`${STAGE_LINK}&file=.context/stories-story-map.md`))
    const stop = page.start()
    await settled()
    return { page, server, stop }
  }

  describe('with a file open and the files of both practices listed', () => {
    it('should send the files listed with the read of the open file', async () => {
      const { page, server, stop } = await opened()
      stop()
      expect(lastRead(server)?.paths).toEqual(paths(page))
    })
  })

  describe('that has DDD turned off', () => {
    it("should read the open file again with the files then listed, DDD's left out", async () => {
      const { page, server, stop } = await opened()
      await page.guidance.toggle('practice', 'ddd')
      await settled()
      stop()
      expect([lastRead(server)?.paths, paths(page)].map(listed => (listed as string[]).includes('.context/ddd-bounded-context.md'))).toEqual([false, false])
    })
  })

  describe("that has observes left out of the graph view's connectors", () => {
    it('should read the open file again with the node filter chosen', async () => {
      const { page, server, stop } = await opened()
      await page.graph.filterTo({ ...page.state.graph.filter, relationships: ['invokes'] })
      await settled()
      stop()
      expect(lastRead(server)?.node_filter).toEqual({ relationships: ['invokes'] })
    })
  })

  describe('that has the graph view reading the graph for a connector left out', () => {
    // The graph view's read as the page's state holds it: under way with the connector chosen, then its trees arrived.
    async function reading(): Promise<{ page: FilesPage; server: FakeFilesServer; readsBefore: number; stop: () => void }> {
      const { page, server, stop } = await opened()
      const readsBefore = server.posted('/file').length
      page.store.change(({ graph }) => ({ graph: { ...graph, isReading: true, filter: { ...graph.filter, relationships: ['invokes'] } } }))
      await settled()
      return { page, server, readsBefore, stop }
    }

    it('should wait for the graph, whose links say what a step invokes and observes', async () => {
      const { server, readsBefore, stop } = await reading()
      stop()
      expect(server.posted('/file')).toHaveLength(readsBefore)
    })

    it('should read the open file again once the trees arrive', async () => {
      const { page, server, readsBefore, stop } = await reading()
      page.store.change(({ graph }) => ({ graph: { ...graph, isReading: false, trees: [] } }))
      await settled()
      stop()
      expect(server.posted('/file').slice(readsBefore).map(post => post.body.node_filter)).toEqual([{ relationships: ['invokes'] }])
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

// The board opens a violation's file here, at the violation's line (proposal 24: the board's own file panel is gone).
describe('Open A File At A Line From A Link', () => {
  const VIOLATION_LINK = `${STAGE_LINK}&file=src%2Forder.py&line=42`

  it('should read the line its link names', () => {
    expect(new FilesLink(VIOLATION_LINK).line).toBe(42)
  })

  it('should read no line from a link that names no file', () => {
    expect(new FilesLink(`${STAGE_LINK}&line=42`).line).toBeNull()
  })

  describe('with the page opened from that link', () => {
    async function opened(): Promise<FilesPage> {
      const page = new FilesPage(new FakeFilesServer(), new FilesLink(VIOLATION_LINK))
      await started(page)
      return page
    }

    it('should open the file the link names', async () => {
      expect((await opened()).state.openPath).toBe('src/order.py')
    })

    it('should show that line of it', async () => {
      expect((await opened()).linesShownIn('src/order.py')).toEqual([{ start: 42, end: 42 }])
    })

    describe('that the Person opens another file from, then the linked file again', () => {
      it('should show no line of it, the link having been followed', async () => {
        const page = await opened()
        await page.open('.context/stories-story-map.md')
        await page.open('src/order.py')
        expect(page.linesShownIn('src/order.py')).toEqual([])
      })
    })
  })
})

// The board's details link the folder a ticket's session works in, as they link its session folder.
describe('Browse The Folder A Session Works In', () => {
  it('should read the workpath folder its link names', () => {
    const link = new FilesLink('?workpath-folder=release-2')
    expect([link.folder, link.ticket, link.isFolder]).toEqual(['workpath', 'release-2', true])
  })

  it("should list the files of the folder the session works in, not its session folder's", async () => {
    const server = new FakeFilesServer()
    await started(new FilesPage(server, new FilesLink('?workpath-folder=release-2')))
    expect([server.posted('/workpath-files').length, server.posted('/folder-files').length]).toEqual([1, 0])
  })
})
