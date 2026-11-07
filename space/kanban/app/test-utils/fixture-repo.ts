import { execFileSync } from 'node:child_process'
import { existsSync, mkdirSync, rmSync, writeFileSync } from 'node:fs'
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

// The graph validate saved beside the story map's report, in the shape harness/graph/saved_graph.py writes (version 2).
const STORY_MAP_NODE = { node_id: 'node-1', name: '', type: 'Story', practice: 'stories', file: STORY_MAP_FILE, line: 6, end_line: 6, stage: '', facts: {} }
const STORY_MAP_HIT = { rule: 'verb-noun-format', message: 'Name the story with a verb', practice: 'stories', node_id: 'node-1', location: STORY_MAP_FILE, line: 6, end_line: 6 }
const STORY_MAP_GRAPH = {
  version: 2,
  overlays: [],
  practices: { stories: { source_root: '', root_facts: {}, nodes: [STORY_MAP_NODE], edges: [], violations: [STORY_MAP_HIT] } },
}

const generated = (practice: string, fidelity: string) => `${STAMP} generate /work ${practice} ${fidelity} markdown ${practice} no-chat`
const validated = (practiceClass: string, fidelity: string) => `${STAMP} validate ${practiceClass} ${fidelity} no-chat`

export function writeInto(path: string, text: string): void {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, text, 'utf-8')
}

export type Session = { name: string; title: string; log?: string[]; folder?: string }

export function writeSession(root: string, { name, title, log = [], folder = name }: Session): void {
  const session = join(root, '.sessions', folder)
  writeInto(join(session, 'session.json'), JSON.stringify({ name, title, scope: 'feature', workpath: root, repo_path: root }))
  writeInto(join(session, 'session.log'), log.map(line => `${line}\n`).join(''))
}

function writeReport(root: string, ticket: string): void {
  const reports = join(root, '.sessions', ticket, 'validation-reports')
  writeInto(join(reports, 'stories-story-map-20261101T100000.md'), '# Graph rule validation\n')
  writeInto(join(reports, 'stories-story-map-20261101T100000.json'), JSON.stringify(STORY_MAP_GRAPH))
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
  writeInto(join(root, '.sessions', 'session.json'), JSON.stringify({ session: 'checkout-flow' }))
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

// Branches a click or an activation opened for a ticket; main is the fixture's own, and git deletes no branch the
// fixture has checked out, so it goes back to main first.
function removeTicketBranches(root: string): void {
  execFileSync('git', ['checkout', '-f', 'main'], { cwd: root, stdio: 'ignore' })
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
  writeInto(join(root, '.gitignore'), '.sessions/\n')
  commitAll(root)
  writeSessions(root)
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) createFixtureRepo(fixtureRoot)
