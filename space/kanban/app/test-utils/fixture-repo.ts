import { execFileSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, realpathSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'

// A throwaway git repository with no remote, so nothing a spec presses can reach real work.
export const fixtureRoot = process.env.BOARD_FIXTURE_ROOT ?? join(tmpdir(), 'cdd-board-surface-fixture')

// The server can still be reading a file when a spec resets, and Windows will not remove one that is open.
const REMOVE_RETRIES = 20
const REMOVE_RETRY_MILLISECONDS = 100
export const STAMP = '2026-11-01T10:00:00Z'
const STORY_MAP_FILE = '.context/story-map.md'
const SOURCE_FILE = 'app/checkout/order.py'
const STORY_MAP_TEXT = ['# Check Out Order', '', '## Payment', '', '- Enter Card Details', '- Handle Payment', '- Confirm Order', ''].join('\n')

// The graph validate saved beside the story map's report, in the shape harness/graph/saved_graph.py writes (version 3).
const STORY_MAP_NODE = { node_id: 'node-1', name: '', type: 'Story', practice: 'stories', file: STORY_MAP_FILE, line: 6, end_line: 6, stage: '', facts: {} }
const STORY_MAP_HIT = { rule: 'verb-noun-format', message: 'Name the story with a verb', practice: 'stories', node_id: 'node-1', location: STORY_MAP_FILE, line: 6, end_line: 6 }
const STORY_MAP_GRAPH = {
  version: 3,
  overlays: [],
  practices: { stories: { source_root: '', root_facts: {}, nodes: [STORY_MAP_NODE], edges: [], violations: [STORY_MAP_HIT] } },
}

const generated = (practice: string, fidelity: string) => `${STAMP} generate /work ${practice} ${fidelity} markdown ${practice} no-chat`
const validated = (practiceClass: string, fidelity: string) => `${STAMP} validate ${practiceClass} ${fidelity} no-chat`

export function writeInto(path: string, text: string): void {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, text, 'utf-8')
}

// A session as its session.json keeps it: a child names its parent, and one pulled out of its parent says so.
export type Session = { name: string; title: string; log?: string[]; folder?: string; parent?: string; pulledOut?: boolean; tags?: string[] }

export function writeSession(root: string, { name, title, log = [], folder = name, parent = '', pulledOut = false, tags = [] }: Session): void {
  const session = join(root, '.sessions', folder)
  writeInto(join(session, 'session.json'), JSON.stringify({ name, title, scope: parent ? 'story' : 'feature', parent, pulled_out: pulledOut, tags, workpath: root, repo_path: root }))
  writeInto(join(session, 'session.log'), log.map(line => `${line}\n`).join(''))
}

function writeReport(root: string, ticket: string): void {
  const reports = join(root, '.sessions', ticket, 'validation-reports')
  writeInto(join(reports, 'stories-story-map-20261101T100000.md'), '# Graph rule validation\n')
  writeInto(join(reports, 'stories-story-map-20261101T100000.json'), JSON.stringify(STORY_MAP_GRAPH))
}

// Every behavior starts with this ticket open, as a chat that opened it leaves the sessions.
const FIRST_OPEN = 'checkout-flow'
// Where the cdd server keeps every chat's open session in its home (space/work_state.py, WorkState).
const OPEN_SESSIONS_FILE = 'open-sessions.json'

// Which session is open is kept by the cdd server in its home, never in the project, as WorkState writes it: an entry for
// the project's folder, since the board's calls name no chat. An empty name opens main, the default session. Written here
// rather than through WorkState, so a reset starts no Python. A run of specs sets CDD_HOME to a throwaway home; without
// one this would write the person's own ~/.cdd, so it refuses.
export function openSession(root: string, ticket: string): void {
  const home = process.env.CDD_HOME
  if (!home) throw new Error("openSession needs the run's throwaway CDD_HOME; it never writes the person's own ~/.cdd")
  const file = join(home, OPEN_SESSIONS_FILE)
  const folder = realpathSync.native(root)
  const kept = existsSync(file) ? (JSON.parse(readFileSync(file, 'utf-8')) as Record<string, Record<string, string>>) : {}
  const { session: _was, ...entry } = kept[`folder:${folder}`] ?? {}
  kept[`folder:${folder}`] = { ...entry, ...(ticket ? { session: ticket } : {}), folder }
  writeInto(file, JSON.stringify(kept, null, 2))
}

function writeSessions(root: string): void {
  writeSession(root, { name: 'checkout-flow', title: 'Checkout flow', log: [generated('stories', 'story_map'), `${STAMP} validate Stories story_map graph-rule verb-noun-format ${STORY_MAP_FILE}:6 no-chat`] })
  writeReport(root, 'checkout-flow')
  writeSession(root, { name: 'billing-report', title: 'Billing report' })
  writeSession(root, { name: 'move-me', title: 'Move me' })
  writeSession(root, { name: 'back-to-backlog', title: 'Back to backlog', log: [generated('stories', 'story_map')] })
  writeSession(root, { name: 'pricing-rules', title: 'Pricing rules', log: [`${STAMP} move Specification no-chat`, generated('stories', 'scenarios'), validated('Stories', 'scenarios')] })
  writeSession(root, { name: 'ready-to-move', title: 'Ready to move', log: [`${STAMP} done Discovery no-chat`] })
  writeSession(root, { name: 'second-spec', title: 'Second spec', log: [`${STAMP} move Specification no-chat`] })
  writeSession(root, { name: 'almost-shipped', title: 'Almost shipped', log: [`${STAMP} move Implementation no-chat`, `${STAMP} done Implementation no-chat`] })
  writeSession(root, { name: 'shipped-work', title: 'Shipped work', folder: join('_complete', 'shipped-work') })
  writeInto(join(root, '.sessions', '_backlog', 'search-the-catalog.md'), '# Search the catalog\n\nAn idea.\n')
  openSession(root, FIRST_OPEN)
}

function commitAll(root: string): void {
  const git = (...args: string[]) => execFileSync('git', args, { cwd: root, stdio: 'ignore' })
  git('init', '-b', 'main')
  git('config', 'user.name', 'Surface Spec')
  git('config', 'user.email', 'surface-spec@example.invalid')
  git('add', '-A')
  git('commit', '-m', 'Fixture')
}

// The sessions a run of specs changes go back to how they started, with no worktree or branch a click opened for a
// ticket. The .git folder and the committed files stay.
export function resetSessions(root: string): void {
  removeWorktrees(root)
  removeTicketBranches(root)
  rmSync(join(root, '.sessions'), { recursive: true, force: true, maxRetries: REMOVE_RETRIES, retryDelay: REMOVE_RETRY_MILLISECONDS })
  writeSessions(root)
}

// Worktrees a spec opened beside the repository outlive it, and a new one of the same name would collide with them.
function removeWorktrees(root: string): void {
  if (!existsSync(join(root, '.git'))) return
  const listed = execFileSync('git', ['worktree', 'list', '--porcelain'], { cwd: root, encoding: 'utf-8' }).split(/\r?\n/)
  const folders = listed.filter(line => line.startsWith('worktree ')).map(line => line.slice('worktree '.length))
  for (const folder of folders.slice(1)) rmSync(folder, { recursive: true, force: true, maxRetries: REMOVE_RETRIES, retryDelay: REMOVE_RETRY_MILLISECONDS })
  // Git keeps a removed folder registered, and will not delete a branch it still counts as checked out there.
  execFileSync('git', ['worktree', 'prune'], { cwd: root, stdio: 'ignore' })
}

// The board saves to git in the background after a change, so a reset right after can meet its index lock for a moment.
function gitRetried(root: string, args: string[]): void {
  for (let attempt = 1; ; attempt++) {
    try {
      execFileSync('git', args, { cwd: root, stdio: 'ignore' })
      return
    } catch (failure) {
      if (attempt >= REMOVE_RETRIES) throw failure
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, REMOVE_RETRY_MILLISECONDS)
    }
  }
}

// Branches a click or an activation opened for a ticket; main is the fixture's own, and git deletes no branch the
// fixture has checked out, so it goes back to main first.
function removeTicketBranches(root: string): void {
  gitRetried(root, ['checkout', '-f', 'main'])
  const branches = execFileSync('git', ['branch', '--format=%(refname:short)'], { cwd: root, encoding: 'utf-8' }).split(/\s+/)
  for (const branch of branches.filter(name => name && name !== 'main')) execFileSync('git', ['branch', '-D', branch], { cwd: root, stdio: 'ignore' })
}

export function createFixtureRepo(root: string): void {
  removeWorktrees(root)
  rmSync(root, { recursive: true, force: true })
  mkdirSync(root, { recursive: true })
  writeInto(join(root, STORY_MAP_FILE), STORY_MAP_TEXT)
  // A folder of code, so a person choosing a root has a folder to pick: the story map's .context is hidden from that list.
  writeInto(join(root, SOURCE_FILE), '')
  // Session folders are the board's record, committed on main; only their logs and chat injections stay out of git.
  writeInto(join(root, '.gitignore'), '.sessions/**/logs/\n.sessions/**/chat-injections/\n')
  writeSessions(root)
  commitAll(root)
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) createFixtureRepo(fixtureRoot)
