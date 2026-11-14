// Switch File Bar Between Folders And List, as
// space/session/files_app/.context/review-files-in-files-app/review_files_in_files_app_story.test.md writes it. Only the
// page shows it: the session answers the same files either way, so it has no step in the Python story tiers.
import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'
import type { FileEntryData } from '@cdd/space/session/session'

import { foldersOf, type FileFolder } from './file-bar'
import { FilesLink } from './files-link'
import { FilesPage } from './files-page'

const STORY_MAP = '.context/story-map.md'
const ORDER = 'src/checkout/order.py'
const CART = 'src/checkout/cart.py'

const entry = (path: string): FileEntryData => ({ path, exists: true, is_changed: false }) as FileEntryData

// The Files app's server, answering the session's files in the order the link names them, and nothing else.
class FakeFilesServer implements CddApi {
  async post<Result>(path: string): Promise<Result | null> {
    if (path.endsWith('/show')) return { practices: {} } as Result
    if (path.endsWith('/files')) return { markdown: [entry(STORY_MAP)], python: [entry(ORDER), entry(CART)] } as Result
    return null
  }
}

// The page with its files listed and order.py open, as the person finds it.
async function pageWithOrderOpen(): Promise<FilesPage> {
  const page = new FilesPage(new FakeFilesServer(), new FilesLink(`?files=checkout-flow&fidelity=stories-story-map&file=${ORDER}`))
  page.start()()
  await new Promise(resolve => setTimeout(resolve, 0))
  return page
}

const named = (folder: FileFolder | undefined): string[] => folder?.files.map(each => each.path) ?? []

function folderShown(page: FilesPage, path: string): FileFolder | undefined {
  return page.fileBar.folders.find(folder => folder.path === path)
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
      it('should show each folder the files are in', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        expect(page.fileBar.folders.map(folder => folder.path)).toEqual(['.context', 'src/checkout'])
      })

      it("should open the open file's folder, showing its files", async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        expect([page.fileBar.isOpen(folderShown(page, 'src/checkout')!), named(folderShown(page, 'src/checkout'))]).toEqual([true, [ORDER, CART]])
      })

      it('should keep every other folder closed', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        expect(page.fileBar.isOpen(folderShown(page, '.context')!)).toBe(false)
      })

      it('should list the files in the order the link names them once shown as a list again', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        page.fileBar.show('list')
        expect([page.state.fileBar.view, page.state.entries.map(each => each.path)]).toEqual(['list', [STORY_MAP, ORDER, CART]])
      })
    })

    describe('that has a closed folder opened', () => {
      it('should show its files', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        page.fileBar.toggleFolder('.context')
        expect(page.fileBar.isOpen(folderShown(page, '.context')!)).toBe(true)
      })

      it('should hide them once closed again', async () => {
        const page = await pageWithOrderOpen()
        page.fileBar.show('folders')
        page.fileBar.toggleFolder('.context')
        page.fileBar.toggleFolder('.context')
        expect(page.fileBar.isOpen(folderShown(page, '.context')!)).toBe(false)
      })
    })
  })
})

describe('folders of the files', () => {
  it('should join a folder that holds only one folder to it, as one path', () => {
    const [docs] = foldersOf([entry('docs/guide/intro.md'), entry('docs/guide/setup.md')])
    expect([docs!.path, named(docs)]).toEqual(['docs/guide', ['docs/guide/intro.md', 'docs/guide/setup.md']])
  })

  it('should keep a file at the top as a folder of no path', () => {
    expect(foldersOf([entry('README.md')]).map(folder => [folder.path, named(folder)])).toEqual([['', ['README.md']]])
  })
})
