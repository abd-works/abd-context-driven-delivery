// Switch File Bar Between Folders And List, as
// harness/.context/stories/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md writes it. Only the
// page shows it: the session answers the same files either way, so it has no step in the Python story tiers.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { FileEntryData } from '@cdd/space/session/session'

import { treeOf, type FileFolder } from './file-bar'
import { FilesLink } from './files-link'
import { FilesPage } from './files-page'

const STORY_MAP = '.context/story-map.md'
const ORDER = 'src/checkout/order.py'
const CART = 'src/checkout/cart.py'

// The files of each fidelity the page asks for, as ticket.fidelity_files answers them.
const byFidelity = (body: Record<string, unknown> | undefined, files: Record<string, FileEntryData[]>) =>
  Object.fromEntries(((body?.fidelities as string[] | undefined) ?? []).map(slug => [slug, files]))

const entry = (path: string, is_changed = false): FileEntryData => ({ path, exists: true, is_changed, link: '', format: '', fidelities: [] }) as FileEntryData

// The Files app's server, answering the session's files in the order the link names them, and nothing else; each file
// the branch changed unless named unchanged, so This session lists it.
class FakeFilesServer implements CddApi {
  constructor(private readonly unchanged: string[] = []) {}

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    if (path.endsWith('/show')) return { practices: {} } as Result
    const changed = (named: string) => entry(named, !this.unchanged.includes(named))
    if (path.endsWith('/fidelity-files')) return byFidelity(body, { markdown: [changed(STORY_MAP)], python: [changed(ORDER), changed(CART)] }) as Result
    return null
  }
}

// The page with its files listed and order.py open, as the person finds it.
async function pageWithOrderOpen(server = new FakeFilesServer()): Promise<FilesPage> {
  const page = new FilesPage(server, new FilesLink(`?files=checkout-flow&fidelity=stories-story-map&file=${ORDER}`))
  page.start()()
  await new Promise(resolve => setTimeout(resolve, 0))
  return page
}

const named = (folder: FileFolder | undefined): string[] => folder?.files.map(each => each.path) ?? []

const allFolders = (folder: FileFolder): FileFolder[] => folder.folders.flatMap(inner => [inner, ...allFolders(inner)])

function folderShown(page: FilesPage, path: string): FileFolder | undefined {
  return allFolders(page.fileBar.tree).find(folder => folder.path === path)
}

describe('Switch File Bar Between Folders And List', () => {
  describe('with order.py open', () => {
    describe('that has the file bar collapsed', () => {
      it('should show only its buttons', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.toggle()
        expect(page.state.fileBar.isOpen).toBe(false)
      })

      it('should list the files again once expanded', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.toggle()
        page.fileBar.toggle()
        expect([page.state.fileBar.isOpen, page.state.entries.map(each => each.path)]).toEqual([true, [STORY_MAP, ORDER, CART]])
      })
    })

    describe('that has the file bar shown as folders', () => {
      it('should show each folder the files are in at the top of the tree', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        expect(page.fileBar.tree.folders.map(folder => folder.name)).toEqual(['.context', 'src/checkout'])
      })

      it("should open the open file's folder, showing its files", async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        expect([page.fileBar.isOpen(folderShown(page, 'src/checkout')!), named(folderShown(page, 'src/checkout'))]).toEqual([true, [CART, ORDER]])
      })

      it('should keep every other folder open, as every folder starts open', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        expect(page.fileBar.isOpen(folderShown(page, '.context')!)).toBe(true)
      })

      it('should list the files in the order the link names them once shown as a list again', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        page.fileBar.show('list')
        expect([page.state.fileBar.view, page.state.entries.map(each => each.path)]).toEqual(['list', [STORY_MAP, ORDER, CART]])
      })
    })

    describe('that has a folder closed', () => {
      it('should hide its files', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.toggleFolder('.context')
        expect(page.fileBar.isOpen(folderShown(page, '.context')!)).toBe(false)
      })

      it('should show them once opened again', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.toggleFolder('.context')
        page.fileBar.toggleFolder('.context')
        expect(page.fileBar.isOpen(folderShown(page, '.context')!)).toBe(true)
      })

      it('should keep it closed once a filter changes the files listed', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.toggleFolder('.context')
        page.store.change(state => ({ entries: state.entries.slice(1) }))
        page.store.change(state => ({ entries: [entry(STORY_MAP, true), ...state.entries] }))
        expect(page.fileBar.isOpen(folderShown(page, '.context')!)).toBe(false)
      })
    })
  })
})

describe('List This Session Or All Session Files', () => {
  describe('with order.py changed and the story map and cart.py not', () => {
    const onlyOrderChanged = () => pageWithOrderOpen(new FakeFilesServer([STORY_MAP, CART]))

    describe('that lists This session, its default', () => {
      it('should list order.py alone', async () => {
        const page = await onlyOrderChanged()
        expect(page.fileBar.entries.map(each => each.path)).toEqual([ORDER])
      })

      it('should show only its folder in the folder tree', async () => {
        const page = await onlyOrderChanged()
        expect(page.fileBar.tree.folders.map(folder => folder.name)).toEqual(['src/checkout'])
      })

      it('should count the one changed file on its button', async () => {
        const page = await onlyOrderChanged()
        expect(page.fileBar.changedCount).toBe(1)
      })
    })
  })

  it('should keep a published design canvas in This session, which opens at its link', () => {
    const canvas = { path: 'design-canvas/version-1/project/canvas.json', exists: true, is_changed: false, link: 'https://claude.ai/artifact/canvas' } as FileEntryData
    const page = new FilesPage(new FakeFilesServer(), new FilesLink('?files=checkout-flow&fidelity=ux-front-end-code'))
    page.store.change(() => ({ entries: [canvas, entry(CART)] }))
    expect(page.fileBar.entries).toEqual([canvas])
  })
})

describe('folder tree of the files', () => {
  it('should nest each folder in the folder it is in', () => {
    const tree = treeOf([entry('src/checkout/order.py'), entry('src/pay/card.py'), entry('src/main.py')])
    expect([tree.folders.map(folder => folder.name), tree.folders[0]!.folders.map(folder => folder.name), named(tree.folders[0])]).toEqual([['src'], ['checkout', 'pay'], ['src/main.py']])
  })

  it('should join a folder that holds only one folder to it, as one row', () => {
    const [docs] = treeOf([entry('docs/guide/intro.md'), entry('docs/guide/setup.md')]).folders
    expect([docs!.path, docs!.name, named(docs)]).toEqual(['docs/guide', 'docs/guide', ['docs/guide/intro.md', 'docs/guide/setup.md']])
  })

  it('should sort folders and files by name, as Explorer does', () => {
    const tree = treeOf([entry('b/z.py'), entry('b/a.py'), entry('a/x.py')])
    expect([tree.folders.map(folder => folder.name), named(tree.folders[1])]).toEqual([['a', 'b'], ['b/a.py', 'b/z.py']])
  })

  it('should keep a file at the top at the top of the tree', () => {
    expect(named(treeOf([entry('README.md')]))).toEqual(['README.md'])
  })

  it('should open every folder down to the open file once shown as folders, a closed one included', async () => {
    const page = new FilesPage(new NestedFilesServer(), new FilesLink(`?files=checkout-flow&fidelity=clean-engineering-code&file=src/checkout/order.py`))
    page.start()()
    await new Promise(resolve => setTimeout(resolve, 0))
    page.fileBar.toggleFolder('src/checkout')
    page.fileBar.show('folders')
    expect(page.state.fileBar.closedFolders).toEqual([])
  })
})

// A server answering files the branch changed in nested folders, src holding a file of its own beside two folders.
class NestedFilesServer implements CddApi {
  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    if (path.endsWith('/show')) return { practices: {} } as Result
    if (path.endsWith('/fidelity-files')) return byFidelity(body, { python: [entry('src/main.py', true), entry('src/checkout/order.py', true), entry('src/pay/card.py', true)] }) as Result
    return null
  }
}
