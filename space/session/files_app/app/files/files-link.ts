import { chatOfPage } from '@cdd/cdd-shared'

import { FIDELITY_QUERY, FILE_QUERY, FILES_QUERY, SESSION_FOLDER_QUERY, SESSION_QUERY } from './files-paths'

// What the page's link names it to show: a session's folder (?session-folder=<ticket>), or the files of a ticket's
// fidelities (?files=<ticket>&fidelity=<slug,slug>); the session.json those files are read through, the file to open
// first, and the chat that opened the page, which comments are sent to.
export class FilesLink {
  readonly ticket: string
  readonly fidelities: string[]
  readonly sessionFile: string
  readonly file: string
  readonly chat: string

  constructor(search: string) {
    const query = new URLSearchParams(search)
    const folder = query.get(SESSION_FOLDER_QUERY) ?? ''
    this.ticket = folder || (query.get(FILES_QUERY) ?? '')
    this.fidelities = folder ? [] : (query.get(FIDELITY_QUERY) ?? '').split(',').map(slug => slug.trim()).filter(Boolean)
    // A ticket's session is kept in the repository's .sessions folder under its name, when the link names none.
    this.sessionFile = query.get(SESSION_QUERY) || (this.ticket ? `.sessions/${this.ticket}/session.json` : '')
    this.file = query.get(FILE_QUERY) ?? ''
    this.chat = chatOfPage(search)
  }

  get namesFiles(): boolean {
    return Boolean(this.ticket && this.sessionFile)
  }

  get isSessionFolder(): boolean {
    return this.fidelities.length === 0
  }

  get subject(): string {
    return this.isSessionFolder ? `.sessions/${this.ticket}` : `${this.ticket} · ${this.fidelities.join(', ')}`
  }
}
