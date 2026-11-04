import { execFileSync } from 'node:child_process'
import { mkdirSync, rmSync, writeFileSync } from 'node:fs'
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
const SOURCE_FILE = 'src/checkout/order.py'
const STORY_MAP_TEXT = ['# Check Out Order', '', '## Payment', '', '- Enter Card Details', '- Handle Payment', '- Confirm Order', ''].join('\n')

const STORY_MAP_GRAPH = {
  practices: {
    stories: {
      nodes: [['node-1', '', 'Story', 'stories', STORY_MAP_FILE, 6, 6]],
      rules: [['verb-noun-format', 'node-1', 'Name the story with a verb']],
    },
  },
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
  writeSession(root, { name: 'shipped-work', title: 'Shipped work', folder: join('closed', 'shipped-work') })
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

// The sessions a run of specs changes go back to how they started. The .git folder and the committed files stay.
export function resetSessions(root: string): void {
  rmSync(join(root, '.sessions'), { recursive: true, force: true, maxRetries: REMOVE_RETRIES, retryDelay: REMOVE_RETRY_MILLISECONDS })
  writeSessions(root)
}

export function createFixtureRepo(root: string): void {
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
