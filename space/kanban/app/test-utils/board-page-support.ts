import { execFileSync } from 'node:child_process'
import { appendFileSync, mkdtempSync, rmSync } from 'node:fs'
import type { Server } from 'node:http'
import { createServer } from 'node:net'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import type { CddConnection } from '@cdd/cdd-connection'
import type { CddApi } from '@cdd/cdd-shared'
import { ChatClientGenerated, type ChatCommandData } from '@cdd/harness/chat/chat'
import { createApp } from '../packages/session-board/app'
import { BoardUpdate } from '@src/session-board/board-update'
import type { Send } from '@src/kanban/board/board-api'
import { BoardPage } from '@src/kanban/board/board-page'
import type { TicketClient } from '@src/kanban/ticket/ticket-client'

import { CddProject } from './behavior-test/cdd-project'
import { STAMP, writeInto, writeSession, type Session } from './fixture-repo'

// Windows holds a folder a moment after the process using it lets go.
const REMOVE_RETRIES = 20
const REMOVE_RETRY_MILLISECONDS = 250
const LOCAL = '127.0.0.1'
const BOARD_HEADER = { 'X-CDD-Board': '1', 'Content-Type': 'application/json' }
const APP_FOLDER = resolve(fileURLToPath(new URL('.', import.meta.url)), '..')
const STATIC_ROOT = join(APP_FOLDER, 'dist')

// The run keeps its chats in one folder of its own (see run-cdd-home.ts). Spec files take turns, so each starts with none.
const separateChats = (): string => {
  const home = dirname(process.env.CDD_CHATS_FOLDER ?? '')
  rmSync(join(home, 'chats'), { recursive: true, force: true })
  return home
}

const freePort = (): Promise<number> =>
  new Promise((done, failed) => {
    const probe = createServer().listen(0, LOCAL, () => {
      const address = probe.address()
      probe.close(() => (typeof address === 'object' && address ? done(address.port) : failed(new Error('no port'))))
    })
  })

// An update really pulls, builds, and installs, so the test server records each step it would run and when it would
// restart, and a spec can make one step fail.
export class UpdateRecord {
  readonly steps: string[] = []
  restarts = 0
  failingStep: string | null = null

  boardUpdate(): BoardUpdate {
    return new BoardUpdate(
      APP_FOLDER,
      () => this.restarts++,
      async (command, args) => {
        const step = [command, ...args].join(' ')
        this.steps.push(step)
        if (this.failingStep && step.includes(this.failingStep)) throw new Error(`${this.failingStep} could not run`)
      },
    )
  }

  clear(): void {
    this.steps.length = 0
    this.restarts = 0
    this.failingStep = null
  }
}

export type Asked = { method: string; path: string; body: Record<string, unknown> | undefined }

// The real session board server, with its generated routes, on its own port. A page's calls pass straight through to it;
// each page keeps the list of what it asked, which is all a spec reads of the traffic.
export class RunningBoard {
  private constructor(
    readonly cdd: CddConnection,
    private readonly origin: string,
    private readonly server: Server,
    readonly updates: UpdateRecord,
  ) {}

  static async on(cdd: CddConnection): Promise<RunningBoard> {
    const port = await freePort()
    const updates = new UpdateRecord()
    const server = await new Promise<Server>(done => {
      const listening = createApp(cdd, port, STATIC_ROOT, updates.boardUpdate()).listen(port, LOCAL, () => done(listening))
    })
    return new RunningBoard(cdd, `http://${LOCAL}:${port}`, server, updates)
  }

  // A page that has not read the board yet, for what a page does before its first read. timed lets a spec decide when
  // each real answer reaches the page, for answers that arrive out of order.
  unreadPage(timed: (send: Send) => Send = send => send): { page: BoardPage; asked: Asked[] } {
    const asked: Asked[] = []
    const send: Send = (path, init) => {
      asked.push({ method: init?.method ?? 'GET', path, body: init?.body ? (JSON.parse(String(init.body)) as Record<string, unknown>) : undefined })
      return fetch(`${this.origin}${path}`, init)
    }
    return { page: new BoardPage(timed(send)), asked }
  }

  // A page that has read the board once, with what it asks from here on.
  async page(): Promise<{ page: BoardPage; asked: Asked[] }> {
    const opened = this.unreadPage()
    await opened.page.reader.refresh()
    opened.asked.length = 0
    return opened
  }

  // How the cdd-board mod reaches the server, for a spec playing a chat.
  readonly api: CddApi = {
    post: async <Result>(path: string, body: Record<string, unknown>): Promise<Result | null> => {
      const response = await fetch(`${this.origin}/api${path}`, { method: 'POST', headers: BOARD_HEADER, body: JSON.stringify(body) })
      return response.ok ? ((await response.json()) as Result) : null
    },
  }

  close(): Promise<void> {
    return new Promise(done => {
      this.server.close(() => done())
      this.server.closeAllConnections()
    })
  }
}

// One chat as its cdd-board mod sees it: it checks in, and takes the commands the board sent it.
export class TestChat {
  constructor(
    private readonly board: RunningBoard,
    readonly id: string,
    private readonly name: string,
    private readonly folder: string,
  ) {}

  // What the chat was given, as a person reads it.
  async checkIn(isBusy = false): Promise<Pick<ChatCommandData, 'kind' | 'text'>[]> {
    return (await this.take(isBusy)).map(({ kind, text }) => ({ kind, text }))
  }

  // Takes the next command and says the chat could not show it, as the mod does when the chat drops it.
  async refuseNext(reason: string): Promise<void> {
    const [command] = await this.take(false)
    if (command) await ChatClientGenerated.named(this.board.api, this.id).confirm(command.message, false, reason)
  }

  // Takes the next command, shows it, and finishes working on it, as the mod does once the chat's turn ends.
  async finishNext(): Promise<void> {
    const [command] = await this.take(false)
    if (!command) return
    const chat = ChatClientGenerated.named(this.board.api, this.id)
    await chat.confirm(command.message, true)
    await chat.finish(command.message)
  }

  private async take(isBusy: boolean): Promise<ChatCommandData[]> {
    return (await ChatClientGenerated.named(this.board.api, this.id).checkIn(isBusy, this.name, this.folder)) ?? []
  }
}

// A throwaway project with a real cdd server, and the session board server on it, shared by one spec file.
export class BoardOnProject {
  private readonly firstCommit: string
  private origin: string | null = null

  private constructor(
    readonly project: CddProject,
    readonly board: RunningBoard,
    private readonly chatsHome: string,
  ) {
    this.firstCommit = this.git('rev-parse', 'HEAD').trim()
  }

  static async start(): Promise<BoardOnProject> {
    const chatsHome = separateChats()
    const project = new CddProject()
    await project.reset()
    return new BoardOnProject(project, await RunningBoard.on(project.cdd), chatsHome)
  }

  get root(): string {
    return this.project.root
  }

  page(): Promise<{ page: BoardPage; asked: Asked[] }> {
    return this.board.page()
  }

  unreadPage(timed?: (send: Send) => Send): { page: BoardPage; asked: Asked[] } {
    return this.board.unreadPage(timed)
  }

  // folder is where the chat works, as its mod reports it: a ticket's chat works in the ticket's worktree.
  chat(id: string, name = '', folder = ''): TestChat {
    return new TestChat(this.board, id, name, folder)
  }

  // A chat checked in and chosen on the page, as a person sees it in the picker.
  async connectChat(page: BoardPage, id = 'chat-1', isBusy = false): Promise<TestChat> {
    const chat = this.chat(id)
    await chat.checkIn(isBusy)
    await page.chat.refresh()
    page.chat.choose(id)
    return chat
  }

  // A chat whose mod has gone: its state is gone with it.
  forgetChat(id: string): void {
    rmSync(join(this.chatsHome, 'chats', id), { recursive: true, force: true })
  }

  writeSession(session: Session): void {
    writeSession(this.root, session)
  }

  write(path: string, text: string): void {
    writeInto(join(this.root, path), text)
  }

  remove(path: string): void {
    rmSync(join(this.root, path), { force: true })
  }

  // What the tools write to a ticket's log after each action, added to what is there.
  logOn(ticket: string, ...entries: string[]): void {
    appendFileSync(join(this.root, '.sessions', ticket, 'session.log'), entries.map(entry => `${STAMP} ${entry} no-chat\n`).join(''), 'utf-8')
  }

  activate(ticket: string | null): Promise<void> {
    return this.project.open(ticket)
  }

  // A ticket's own worktree beside the project, as activating it with a worktree leaves it. Returns its folder.
  openWorktree(ticket: string): string {
    const folder = `${this.root}-${ticket}`
    this.git('worktree', 'add', '-b', ticket, folder)
    return folder
  }

  // A branch checked out in a worktree cannot be deleted, so the worktrees go first.
  private removeWorktrees(): void {
    const lines = this.git('worktree', 'list', '--porcelain').split(/\r?\n/)
    const folders = lines.filter(line => line.startsWith('worktree ')).map(line => line.slice('worktree '.length))
    // On Windows git can unregister a worktree and leave its folder, which the next one of that name then collides with.
    for (const folder of folders.slice(1)) {
      this.git('worktree', 'remove', '--force', folder)
      rmSync(folder, { recursive: true, force: true, maxRetries: REMOVE_RETRIES, retryDelay: REMOVE_RETRY_MILLISECONDS })
    }
  }

  // The active ticket on a branch of its own, as activating it with a branch leaves it.
  checkOutBranch(name: string): void {
    this.git('checkout', '-b', name)
  }

  // A bare repository in a temporary folder as the project's origin, so leaving a session can push and merge for real.
  addOrigin(): void {
    this.origin = mkdtempSync(join(tmpdir(), 'cdd-board-page-origin-'))
    execFileSync('git', ['init', '--bare', '-b', 'main', this.origin], { stdio: 'ignore' })
    this.git('remote', 'add', 'origin', this.origin)
    this.git('push', '-u', 'origin', 'main')
  }

  private removeOrigin(): void {
    if (!this.origin) return
    this.git('remote', 'remove', 'origin')
    rmSync(this.origin, { recursive: true, force: true })
    this.origin = null
  }

  git(...args: string[]): string {
    return execFileSync('git', args, { cwd: this.root, encoding: 'utf-8', stdio: ['ignore', 'pipe', 'ignore'] })
  }

  // Sessions, chats, branches, and the origin back to how they started, for a spec that changed them.
  async reset(): Promise<void> {
    const hadOrigin = this.origin !== null
    this.removeOrigin()
    this.removeWorktrees()
    this.git('checkout', '-f', 'main')
    this.git('reset', '--hard', this.firstCommit)
    this.git('clean', '-fd')
    for (const branch of this.git('branch', '--format=%(refname:short)').split('\n').filter(name => name && name !== 'main')) this.git('branch', '-D', branch)
    rmSync(join(this.chatsHome, 'chats'), { recursive: true, force: true })
    await this.project.reset()
    this.board.updates.clear()
    if (hadOrigin) this.addOrigin()
  }

  async close(): Promise<void> {
    this.removeOrigin()
    this.removeWorktrees()
    await this.board.close()
    await this.project.close()
    rmSync(this.chatsHome, { recursive: true, force: true })
  }
}

export const ticketOn = (page: BoardPage, name: string): TicketClient => {
  const found = page.board.tickets.find(ticket => ticket.name === name && ticket.column.name !== 'Complete')
  if (!found) throw new Error(`The board shows no open ticket ${name}`)
  return found
}
