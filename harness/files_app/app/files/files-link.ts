import { chatOfPage, projectOfPage } from '@cdd/cdd-shared'

import { FIDELITY_QUERY, FILE_QUERY, FILES_QUERY, LINE_QUERY, SESSION_FOLDER_QUERY, SESSION_QUERY, WORKPATH_FOLDER_QUERY } from './files-paths'

// The folder a link lists every file of: the ticket's session folder, or the folder its session works in.
export type LinkedFolder = 'session' | 'workpath' | ''

// What the page's link names it to show: a session's folder (?session-folder=<ticket>), the folder that session works in
// (?workpath-folder=<ticket>), or the files of a ticket's fidelities (?files=<ticket>&fidelity=<slug,slug>); the
// session.json those files are read through, the file to open first and the line of it to show (&file=<path>&line=<n>),
// and the chat that opened the page, which comments are sent to.
export class FilesLink {
  readonly ticket: string
  readonly folder: LinkedFolder
  readonly fidelities: string[]
  readonly sessionFile: string
  readonly file: string
  readonly line: number | null
  readonly chat: string
  readonly project: string

  constructor(search: string) {
    const query = new URLSearchParams(search)
    const sessionFolder = query.get(SESSION_FOLDER_QUERY) ?? ''
    const workpathFolder = query.get(WORKPATH_FOLDER_QUERY) ?? ''
    this.folder = sessionFolder ? 'session' : workpathFolder ? 'workpath' : ''
    this.ticket = sessionFolder || workpathFolder || (query.get(FILES_QUERY) ?? '')
    this.fidelities = this.folder ? [] : (query.get(FIDELITY_QUERY) ?? '').split(',').map(slug => slug.trim()).filter(Boolean)
    // A ticket's session is kept in the repository's .sessions folder under its name, when the link names none.
    this.sessionFile = query.get(SESSION_QUERY) || (this.ticket ? `.sessions/${this.ticket}/session.json` : '')
    this.file = query.get(FILE_QUERY) ?? ''
    const line = Number(query.get(LINE_QUERY))
    this.line = this.file && Number.isInteger(line) && line > 0 ? line : null
    this.chat = chatOfPage(search)
    this.project = projectOfPage(search)
  }

  get namesFiles(): boolean {
    return Boolean(this.ticket && this.sessionFile)
  }

  // A link to a folder lists every file in it; a link to fidelities lists theirs, by the session's guidance selection.
  get isFolder(): boolean {
    return this.fidelities.length === 0
  }

  get subject(): string {
    if (this.folder === 'workpath') return `the folder ${this.ticket} works in`
    return this.isFolder ? `.sessions/${this.ticket}` : this.ticket
  }

  // The line of path the link asks to show, once: the link's file at its line.
  linesIn(path: string): { start: number; end: number }[] {
    return this.line !== null && path === this.file ? [{ start: this.line, end: this.line }] : []
  }
}
