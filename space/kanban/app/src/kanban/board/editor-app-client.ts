import { CHAT_QUERY, PROJECT_QUERY, type CddApi } from '@cdd/cdd-shared'
import { AppClientGenerated, type AppData } from '@cdd/harness/diagnostics/app'

import type { Failures } from './board-api'

// The apps' identities, the labels they registered under, as their generated clients name them.
const GRAPH_APP = 'Graph'
const KANBAN_APP = 'Kanban'
const FILES_APP = 'Files'

// The words the Files app's link names what it shows with (harness/files_app/app/files/files-paths.ts).
const FILES_QUERY = 'files'
const FIDELITY_QUERY = 'fidelity'
const SESSION_FOLDER_QUERY = 'session-folder'
const WORKPATH_FOLDER_QUERY = 'workpath-folder'
const SESSION_QUERY = 'session'
const FILE_QUERY = 'file'
const LINE_QUERY = 'line'

// The ticket the Files app opens on: its name, the session.json its files are read through, and the chat working on it,
// which the app's comments are sent to.
export type FilesTicket = { name: string; session: { session_file: string }; workingChat: { id: string } | null }

// What the Files app shows of a ticket: the files of some of its fidelities, by slug, or every file of its session folder
// or of the folder its session works in; with a file of them open, at a line, such as a violation's.
export type FilesPlace = ({ fidelities: string[] } | { folder: 'session' | 'workpath' }) & { file?: string; line?: number }

// Opens any App in a window of its own on a project: a ticket's worktree, where that ticket's session is the open one, or
// the board's own project from the header, whose open session is the board's active ticket. Every call the app then
// makes works in that session. The Story UI editor opens from the Stories story-map row (Python's BoardFidelity.editor
// names it), the Graph app from the header and from each ticket's graph widget, and the Files app wherever the board links
// a ticket's files: a card's or a tile's files button, the details' folder links, and a violation's place in a report.
// Python's App.open readies the app and says where it answers; the chat that opened it runs its server.
export class EditorAppClient {
  readonly graph: AppClientGenerated
  // The board itself, which Update installs again, rebuilding the page this board loads.
  readonly kanban: AppClientGenerated
  // The file viewer, harness/files_app: the board shows no file itself.
  readonly files: AppClientGenerated

  constructor(
    private readonly failures: Failures,
    private readonly api: CddApi,
    private readonly project: () => string,
    private readonly openWindow: (url: string) => void = url => void window.open(url, '_blank'),
  ) {
    this.graph = AppClientGenerated.named(api, GRAPH_APP)
    this.kanban = AppClientGenerated.named(api, KANBAN_APP)
    this.files = AppClientGenerated.named(api, FILES_APP)
  }

  // Opens the Files app on what place names of the ticket, in the board's project, where the ticket's session.json is.
  async openFilesOn(ticket: FilesTicket, place: FilesPlace): Promise<void> {
    const shown: [string, string][] = 'folder' in place
      ? [[place.folder === 'session' ? SESSION_FOLDER_QUERY : WORKPATH_FOLDER_QUERY, ticket.name]]
      : [[FILES_QUERY, ticket.name], [FIDELITY_QUERY, place.fidelities.join(',')]]
    const file: [string, string][] = place.file ? [[FILE_QUERY, place.file], ...(place.line ? [[LINE_QUERY, String(place.line)] as [string, string]] : [])] : []
    await this.openOn(this.files, this.project(), ticket.workingChat?.id ?? '', [...shown, [SESSION_QUERY, ticket.session.session_file], ...file])
  }

  // The editor a practice row names, as the board read sent it.
  editorOf(editor: AppData): AppClientGenerated {
    return new AppClientGenerated(this.api, editor)
  }

  // chat names the ticket's chat, when it has one, so the app can show a file in that chat's file viewer, as the Story
  // UI editor shows a story's acceptance tests.
  async openOn(app: AppClientGenerated, project: string, chat: string = '', query: [string, string][] = []): Promise<void> {
    const opened = await app.open()
    if (!opened) return
    if (opened.status !== 'running') {
      this.failures.fail(`The ${opened.label} app is ${opened.status}: open it from the chat bar's status row, which starts it for that chat.`, `Opening the ${opened.label} app from the Kanban board`)
      return
    }
    const page = new URL(opened.url)
    page.searchParams.set(PROJECT_QUERY, project)
    if (chat) page.searchParams.set(CHAT_QUERY, chat)
    for (const [name, value] of query) page.searchParams.set(name, value)
    this.openWindow(page.toString())
  }
}
