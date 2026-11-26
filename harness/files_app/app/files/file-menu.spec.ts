// The Files app's acceptance tests for what only the page shows of the file menu's actions and the All files scope, story by
// story as story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md
// and filter-files-in-files-app/filter_files_in_files_app_story.test.md write them. What the session answers, which
// paths may be deleted, what a root is, and which files are in the session's folders, is proved by the Python specs
// (space/session/files/session_files_spec.py, space/session/practices/practice_session_output_spec.py,
// space/session/validation/changed_artifact_spec.py, space/kanban/kanban_tools_spec.py).
import { render } from '@testing-library/react'
import { createElement } from 'react'
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'

import { FilesLink } from './files-link'
import { FilesPage } from './files-page'
import { FilesPageView } from './files-page-view'

// Seed: the session's practices as session.show answers them, Stories having a file a person added as a root.
const practiceOf = (name: string, short_name: string, added_roots: string[] = []) => ({ name, session_file: '.sessions/release-2/session.json', short_name, colour: '#c0392b', added_roots })
const STORIES = practiceOf('stories', 'Stories', ['c/vb/hr/e/story-1.md'])
const DDD = practiceOf('ddd', 'DDD')
// Seed: the files under the session's root, as ticket.root_files answers them: two the selection lists, one it does not.
const fileOf = (path: string, is_listed = true) => ({ path, exists: true, is_changed: false, link: '', format: 'markdown', fidelities: [], is_listed, is_session_work: false, hidden_by_formats: [] })
const ROOT_FILES = [fileOf('.context/story-map.md'), fileOf('docs/notes.md'), fileOf('docs/plain.txt', false)]
// Seed: every file in the session's folders, as session.all_files answers them, a root a person added among them.
const ALL_FILES = [...ROOT_FILES, fileOf('c/vb/hr/e/story-1.md'), fileOf('scratch/todo.txt')]
// Seed: the story map's violation of verb-noun-format at line 12, as ticket.violations_of answers it.
const VIOLATION = { rule: 'verb-noun-format', practice: 'stories', node_id: 'node-1', subject: '', location: '.context/story-map.md', line: 12, end_line: 12, message: 'Name the story with a verb', severity: 'violation', scope: '', source: [] }
const VIOLATIONS = { path: '.sessions/release-2/validation-reports', rules: [{ fidelity: { slug: 'stories-story-map' }, rule: { slug: 'verb-noun-format' }, count: 1, violations: [VIOLATION] }] }

const LINK = '?files=release-2&fidelity=stories-story-map&chat=chat-1'

// The Files app's page against a fake of its own server: each post answers what the route would, and is kept in order.
class FakeFilesServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = []
  practices = [STORIES, DDD]
  refused: Record<string, string> = {}

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body })
    const refusal = Object.entries(this.refused).find(([ending]) => path.endsWith(ending))
    if (refusal) throw new Error(refusal[1])
    if (path.endsWith('/show')) return { name: 'release-2', repo_name: 'abd-cdd', branch: 'release-2', root: 'C:/dev/abd-cdd-2', practices: Object.fromEntries(this.practices.map(each => [each.name, each])) } as Result
    if (path.endsWith('/guidance-selection')) return { version: 1, stages: [], practices: [], formats: [], fidelities: ['stories-story-map'] } as Result
    if (path.endsWith('/guidance-selection-after')) return new Promise(() => undefined)
    if (path.endsWith('/fidelity-files')) return { 'stories-story-map': { markdown: [fileOf('.context/story-map.md')] } } as Result
    if (path.endsWith('/root-files')) return ROOT_FILES as Result
    if (path.endsWith('/all-files')) return ALL_FILES as Result
    if (path.endsWith('/delete-file')) return body.path as Result
    if (path.endsWith('/check-changed-artifact')) return { path: body.path, checked: String(body.path).startsWith('docs') ? [] : ['stories-story-map'] } as Result
    if (path.endsWith('/violations-of')) return (String(body.path).startsWith('docs') ? { ...VIOLATIONS, rules: [] } : VIOLATIONS) as Result
    if (path.endsWith('/add-root')) return this.added(path, String(body.path)) as Result
    return null
  }

  // practice-session-output.add_root: the path kept among the practice's added roots.
  private added(path: string, root: string) {
    const practice = this.practices.find(each => path.includes(`/${each.name}/`))!
    const changed = { ...practice, added_roots: [...practice.added_roots, root] }
    this.practices = this.practices.map(each => (each === practice ? changed : each))
    return changed
  }

  posted(ending: string): { path: string; body: Record<string, unknown> }[] {
    return this.posts.filter(post => post.path.endsWith(ending))
  }
}

async function settled(): Promise<void> {
  for (let turn = 0; turn < 8; turn += 1) await new Promise(resolve => setTimeout(resolve, 0))
}

// The page as the person finds it once it opened, with the menu on path where the Person right-clicked.
async function rightClicked(path: string, server = new FakeFilesServer()): Promise<{ page: FilesPage; server: FakeFilesServer }> {
  const page = new FilesPage(server, new FilesLink(LINK))
  page.start()()
  await settled()
  page.menu.open(path, 40, 80)
  return { page, server }
}

const toldTheChat = (server: FakeFilesServer): string[] => server.posted('/send').map(post => JSON.parse(String(post.body.text)).failure)

describe('Delete File Or Folder From File Menu', () => {
  describe('with the Person choosing Delete on a file', () => {
    async function askedToDelete(server?: FakeFilesServer) {
      const opened = await rightClicked('docs/notes.md', server)
      opened.page.menu.askToDelete()
      return opened
    }

    it('should ask to confirm, saying it cannot be undone', async () => {
      expect((await askedToDelete()).page.menu.confirmation).toBe('Delete docs/notes.md? This cannot be undone.')
    })

    it('should delete nothing before the Person confirms', async () => {
      expect((await askedToDelete()).server.posted('/delete-file')).toEqual([])
    })

    describe('that the Person confirms', () => {
      async function confirmed(server?: FakeFilesServer) {
        const opened = await askedToDelete(server)
        await opened.page.menu.confirmDelete()
        return opened
      }

      it('should ask the session to delete it', async () => {
        expect((await confirmed()).server.posted('/delete-file').map(post => post.body.path)).toEqual(['docs/notes.md'])
      })

      it('should read the file list again', async () => {
        const { server } = await askedToDelete()
        const listedBefore = server.posted('/root-files').length
        await (await rightClicked('docs/notes.md', server)).page.menu.confirmDelete()
        expect(server.posted('/root-files').length).toBeGreaterThan(listedBefore)
      })

      it('should close the menu and the confirmation', async () => {
        expect((await confirmed()).page.state.menu).toBeNull()
      })

      describe('with the session refusing it', () => {
        it('should tell the chat that opened the page, with the reason', async () => {
          const server = new FakeFilesServer()
          server.refused['/delete-file'] = 'docs/notes.md is outside the session\'s roots'
          const { server: told } = await confirmed(server)
          expect(toldTheChat(told)).toContain("docs/notes.md was not deleted: docs/notes.md is outside the session's roots")
        })
      })
    })

    describe('that the Person cancels', () => {
      it('should delete nothing and close the menu', async () => {
        const { page, server } = await askedToDelete()
        page.menu.close()
        expect([page.state.menu, server.posted('/delete-file')]).toEqual([null, []])
      })
    })
  })
})

describe('Validate File Or Folder From File Menu', () => {
  it('should ask the session to validate the file or folder', async () => {
    const { page, server } = await rightClicked('.context')
    await page.menu.validate()
    expect(server.posted('/check-changed-artifact').map(post => post.body.path)).toEqual(['.context'])
  })

  it('should say which fidelities checked it', async () => {
    const { page } = await rightClicked('.context/story-map.md')
    await page.menu.validate()
    expect(page.state.toasts).toContain('Validated .context/story-map.md with stories-story-map')
  })

  it('should say so when no fidelity the session shows declares it', async () => {
    const { page } = await rightClicked('docs/notes.md')
    await page.menu.validate()
    expect(page.state.toasts).toContain('No fidelity the session shows declares docs/notes.md')
  })
})

describe('Display Violations Of File Or Folder', () => {
  it('should show the rules the reports find broken in it', async () => {
    const { page } = await rightClicked('.context/story-map.md')
    await page.menu.showViolations()
    expect(page.state.violations?.report.rules.map(rule => rule.rule.slug)).toEqual(['verb-noun-format'])
  })

  it('should ask the ticket for the violations of that path', async () => {
    const { page, server } = await rightClicked('.context')
    await page.menu.showViolations()
    expect(server.posted('/violations-of').map(post => post.body.path)).toEqual(['.context'])
  })

  it('should say so when no rule is broken there', async () => {
    const { page } = await rightClicked('docs/notes.md')
    await page.menu.showViolations()
    expect(page.violationsNote).toBe('No rule is broken in docs/notes.md')
  })

  describe('with a violation the Person presses', () => {
    it('should open its file at its line', async () => {
      const { page } = await rightClicked('.context/story-map.md')
      await page.menu.showViolations()
      await page.openViolation(VIOLATION)
      expect([page.state.openPath, page.linesShownIn('.context/story-map.md')]).toEqual(['.context/story-map.md', [{ start: 12, end: 12 }]])
    })
  })
})

describe('Add File Or Folder To Practice', () => {
  it("should offer the session's practices", async () => {
    const { page } = await rightClicked('src/orders/refund')
    expect(page.state.practices.map(practice => practice.short_name)).toEqual(['Stories', 'DDD'])
  })

  describe('with the Person choosing DDD', () => {
    async function added() {
      const opened = await rightClicked('src/orders/refund')
      await opened.page.menu.addToPractice(opened.page.state.practices[1]!)
      return opened
    }

    it("should ask DDD's practice to add the folder as a root", async () => {
      const { server } = await added()
      expect(server.posted('/add-root').map(post => [post.path, post.body.path])).toEqual([['/practice-session-output/.sessions%2Frelease-2%2Fsession.json/ddd/add-root', 'src/orders/refund']])
    })

    it('should show the root the practice now has', async () => {
      expect((await added()).page.fileBar.addedRoots).toEqual(['c/vb/hr/e/story-1.md', 'src/orders/refund'])
    })

    it('should say what was added', async () => {
      expect((await added()).page.state.toasts).toContain('src/orders/refund added to DDD')
    })
  })
})

describe('List Every File In Session Folders', () => {
  async function everything() {
    const page = new FilesPage(new FakeFilesServer(), new FilesLink(LINK))
    page.start()()
    await settled()
    page.showScope('everything')
    await settled()
    return page
  }

  it('should list every file in the session\'s folders, those the selection leaves out among them', async () => {
    expect((await everything()).fileBar.entries.map(entry => entry.path)).toEqual(ALL_FILES.map(file => file.path))
  })

  it('should show a root a person added at the top of the folder tree, under its own name', async () => {
    const page = await everything()
    expect(page.fileBar.tree.files.map(entry => entry.path)).toEqual(['c/vb/hr/e/story-1.md'])
  })

  // Found by the e2e twin (act-on-files-from-file-menu.story.ui_e2e_spec.py): a session whose formats chosen leave out
  // every file it declares listed nothing in All files, saying none of the files is in the formats chosen.
  describe('with the selection listing no file', () => {
    class NothingSelectedServer extends FakeFilesServer {
      override async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
        if (path.endsWith('/fidelity-files')) return {} as Result
        if (path.endsWith('/root-files')) return [] as Result
        return super.post<Result>(path, body)
      }
    }

    it("should draw every file in the session's folders", async () => {
      const page = new FilesPage(new NothingSelectedServer(), new FilesLink(LINK))
      const view = render(createElement(FilesPageView, { page }))
      await settled()
      page.showScope('everything')
      await settled()
      const drawn = [...view.container.querySelectorAll('button.file-entry')].map(entry => entry.getAttribute('title'))
      view.unmount()
      expect(drawn.sort()).toEqual(ALL_FILES.map(file => file.path).sort())
    })
  })

  describe('that the Person leaves for All session files', () => {
    it('should list again only the files the selection lists', async () => {
      const page = await everything()
      page.showScope('all')
      await settled()
      expect(page.fileBar.entries.map(entry => entry.path)).toEqual(['.context/story-map.md', 'docs/notes.md'])
    })
  })
})
