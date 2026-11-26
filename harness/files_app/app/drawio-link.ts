import { existsSync, readFileSync, statSync } from 'node:fs'
import { dirname, isAbsolute, join, relative, resolve } from 'node:path'

import { FILE_QUERY, FILES_QUERY, LINE_QUERY } from './files/files-paths'

// The ticket a link from a diagram lists files of when the viewer was opened with none, as the board's main session is.
const MAIN_TICKET = 'main'

// The anchor GitHub and VS Code give a heading, as the story map writes its links (heading_anchor in
// cdd_guidance/practices/stories/model/markdown/links.py): links reduced to their labels, lower case, punctuation
// dropped, spaces as hyphens; a repeated heading takes -1, -2 as GitHub does.
export const headingAnchorOf = (heading: string): string =>
  heading
    .replace(/\[([^\]\n]+)\]\([^)\s]*\)/g, '$1')
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}_\- ]/gu, '')
    .replace(/ /g, '-')

// The 1-based line of the heading in text whose anchor is anchor; the first line when anchor is empty or no heading has it.
export function headingLineOf(text: string, anchor: string): number {
  if (!anchor) return 1
  const seen = new Map<string, number>()
  const lines = text.split(/\r?\n/)
  for (let index = 0; index < lines.length; index += 1) {
    const heading = /^#+ (.+)$/.exec(lines[index])
    if (!heading) continue
    const plain = headingAnchorOf(heading[1])
    const count = seen.get(plain)
    seen.set(plain, count === undefined ? 0 : count + 1)
    if ((count === undefined ? plain : `${plain}-${count + 1}`) === anchor) return index + 1
  }
  return 1
}

// A link a cell of a draw.io diagram carries, such as ../story_tests/a/b_story.test.md or story-map.md#e-register, read
// beside the diagram, as the story map writes it. The draw.io viewer sends a press on it here, since the viewer serves
// only diagrams; the Files app shows the file it names, at the heading its anchor names.
export class DrawioLink {
  readonly target: string
  readonly anchor: string

  constructor(
    readonly diagram: string,
    readonly link: string,
    readonly project: string,
  ) {
    const [path, anchor = ''] = link.split('#', 2)
    this.anchor = decodeURIComponent(anchor)
    const diagramPath = isAbsolute(diagram) ? diagram : join(project, diagram)
    this.target = resolve(dirname(diagramPath), decodeURIComponent(path))
  }

  // Whether the file the link names is there to show.
  get isThere(): boolean {
    return existsSync(this.target) && statSync(this.target).isFile()
  }

  // The file named from the project's root, as the Files app takes it; its whole path when it sits outside the project.
  get file(): string {
    const fromProject = relative(this.project, this.target)
    return fromProject && !fromProject.startsWith('..') && !isAbsolute(fromProject) ? fromProject.split('\\').join('/') : this.target.split('\\').join('/')
  }

  // The Files app's page on the file, at the heading the link's anchor names, for ticket's files.
  pageOf(ticket: string, chat: string): string {
    const query = new URLSearchParams({ [FILES_QUERY]: ticket || MAIN_TICKET, project: this.project, [FILE_QUERY]: this.file })
    query.set(LINE_QUERY, String(headingLineOf(readFileSync(this.target, 'utf-8'), this.anchor)))
    if (chat) query.set('chat', chat)
    return `/?${query.toString()}`
  }

  // What the person is told when the link names a file that is not there.
  get missing(): string {
    return `The link ${this.link} in ${this.diagram} names ${this.target}, which is not there`
  }
}
