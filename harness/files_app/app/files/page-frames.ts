import type { CddApi } from '@cdd/cdd-shared'

import { FilesCallFailure } from './files-api'
import { PAGE_FILES } from './files-paths'

const HEAD_OPENING = /<head(\s[^>]*)?>/i
const escapedAttribute = (text: string): string => text.replace(/&/g, '&amp;').replace(/"/g, '&quot;')

// An HTML page with a base address in front of everything it loads, so the scripts, styles and images it names from its
// own folder, and the Story Demo scripts a UX mockup names from /practices/ux/story-demo, are asked of the Files server.
export function pageWithBase(html: string, base: string): string {
  const tag = `<base href="${escapedAttribute(base)}">`
  const head = HEAD_OPENING.exec(html)
  if (!head) return `${tag}${html}`
  const after = head.index + head[0].length
  return `${html.slice(0, after)}${tag}${html.slice(after)}`
}

// The folder of a file named from its project's root, as the path part of an address, each name in it encoded.
const folderAddressOf = (path: string): string =>
  path
    .split('/')
    .slice(0, -1)
    .map(name => `${encodeURIComponent(name)}/`)
    .join('')

// The frames the Files app shows HTML pages in: each page runs its own scripts in a frame of no origin, apart from the
// Files app, and finds the files it names in its project through the Files server, under the key the server made for
// the project. The key is asked for once, when the first page shows, and again after an ask that failed.
export class PageFrames {
  private projectBase: Promise<string> | null = null

  constructor(private readonly api: CddApi) {}

  // The page of the file at path, as its frame shows it: with the address of its own folder in front of what it loads.
  async pageOf(path: string, html: string): Promise<string> {
    const base = new URL(`${await this.baseOfProject()}${folderAddressOf(path)}`, window.location.href)
    return pageWithBase(html, base.href)
  }

  private baseOfProject(): Promise<string> {
    this.projectBase ??= this.api.post<{ base: string }>(PAGE_FILES, {}).then(answer => {
      if (!answer?.base) throw new FilesCallFailure(`${PAGE_FILES} answered no address for the project's files`)
      return answer.base
    })
    this.projectBase.catch(() => (this.projectBase = null))
    return this.projectBase
  }
}
