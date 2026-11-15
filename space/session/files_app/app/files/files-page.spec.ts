// The Files app's acceptance tests for what only the page shows, story by story as
// harness/.context/stories/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md writes them; what the
// session answers is proved by space/session/files_app/review-files-in-files-app.story.domain.spec.py.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { GuidanceSelectionData } from '@cdd/space/session/session'

import { FilesLink } from './files-link'
import { FilesPage, filesShown } from './files-page'
import { drawioPageOf } from './files-paths'

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
  private readonly waiting: (() => void)[] = []

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    if (path.endsWith('/guidance-selection')) return this.selection() as Result
    if (path.endsWith('/show')) return { name: 'release-2', repo_name: 'abd-cdd', branch: 'release-2', root: 'C:/dev/abd-cdd-2' } as Result
    if (path.endsWith('/update-guidance-selection')) return this.update(body) as Result
    if (path.endsWith('/guidance-selection-after')) return (await this.after(Number(body.version))) as Result
    if (path.endsWith('/fidelity-files')) return Object.fromEntries((body.fidelities as string[]).map(slug => [slug, { markdown: [entry(`.context/${slug}.md`)], drawio: [entry(`.context/${slug}.drawio`)] }])) as Result
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
    const fidelities = Object.keys(FIDELITIES).filter(stage => chosen.includes(stage)).flatMap(stage => this.practices.map(key => FIDELITIES[stage]![key]).filter((slug): slug is string => Boolean(slug)))
    return {
      version: this.version,
      is_stage_chosen: this.stages !== null,
      stages: Object.keys(FIDELITIES).map(name => ({ name, title: name.charAt(0).toUpperCase() + name.slice(1), is_selected: chosen.includes(name) })),
      practices: PRACTICES.map(practice => ({ ...practice, is_selected: this.practices.includes(practice.key) })),
      formats: [
        { label: 'markdown', formats: ['markdown'], offered: fidelities.length, is_selected: this.formats.includes('markdown') },
        { label: 'diagram', formats: ['drawio'], offered: fidelities.length, is_selected: this.formats.includes('diagram') },
      ],
      fidelities,
    } as GuidanceSelectionData
  }

  posted(ending: string): { path: string; body: Record<string, unknown> }[] {
    return this.posts.filter(post => post.path.endsWith(ending))
  }
}

function entry(path: string) {
  return { path, exists: true, is_changed: false, link: '' } as never
}

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
        await page.togglePractice('ddd')
        stop()
        expect(server.posted('/update-guidance-selection').map(post => post.body.practices)).toEqual([['stories']])
      })

      it("should list only Stories' files", async () => {
        const { page, stop } = await following(discovery())
        await page.togglePractice('ddd')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.md', '.context/stories-story-map.drawio'])
      })
    })

    describe('that has Specification selected in the Files app', () => {
      it("should list both stages' files, reading Specification's the first time it shows", async () => {
        const { page, stop } = await following(discovery())
        await page.toggleStage('specification')
        await settled()
        stop()
        expect(paths(page)).toContain('.context/stories-scenarios.md')
      })
    })

    describe('that has the diagram format selected in the Files app', () => {
      it('should list only the diagrams', async () => {
        const { page, stop } = await following(discovery())
        await page.toggleFormat('diagram')
        await settled()
        stop()
        expect(paths(page)).toEqual(['.context/stories-story-map.drawio', '.context/ddd-bounded-context.drawio'])
      })
    })

    describe('that has every stage turned off', () => {
      it('should list no file', async () => {
        const { page, stop } = await following(discovery())
        await page.toggleStage('discovery')
        await settled()
        stop()
        expect(paths(page)).toEqual([])
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
        await page.togglePractice('ddd')
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
  describe('that has All session files pressed', () => {
    it('should list the files of the stages selected that the branch has not changed', async () => {
      const server = new FakeFilesServer()
      server.stages = ['discovery']
      const { page, stop } = await following(server)
      page.showScope('all')
      stop()
      expect(page.fileBar.entries.map(each => each.path)).toContain('.context/stories-story-map.md')
    })

    it('should list only the files in the formats selected', async () => {
      const server = new FakeFilesServer()
      server.stages = ['discovery']
      server.formats = ['diagram']
      const { page, stop } = await following(server)
      page.showScope('all')
      stop()
      expect(page.fileBar.entries.every(each => each.path.endsWith('.drawio'))).toBe(true)
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
