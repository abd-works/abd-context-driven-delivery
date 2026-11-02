import { execFileSync } from 'node:child_process'
import { mkdirSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { pathToFileURL } from 'node:url'

// A throwaway git repository with no remote, so nothing a surface spec presses can reach real work.
export const fixtureRoot = process.env.BOARD_FIXTURE_ROOT ?? join(tmpdir(), 'cdd-board-surface-fixture')

const STAMP = '2026-11-01T10:00:00Z'
const STORY_MAP_FILE = 'tests/story-map.md'
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

function writeInto(path: string, text: string): void {
  mkdirSync(dirname(path), { recursive: true })
  writeFileSync(path, text, 'utf-8')
}

function writeSession(root: string, name: string, title: string, logLines: string[], folder = name): void {
  const session = join(root, '.sessions', folder)
  writeInto(join(session, 'session.json'), JSON.stringify({ name, title, scope: 'feature', workpath: root, repo_path: root }))
  writeInto(join(session, 'session.log'), logLines.map(line => `${line}\n`).join(''))
}

function writeReport(root: string, ticket: string): void {
  const reports = join(root, '.sessions', ticket, 'validation-reports')
  writeInto(join(reports, 'stories-story-map-20261101T100000.md'), '# Graph rule validation\n')
  writeInto(join(reports, 'stories-story-map-20261101T100000.json'), JSON.stringify(STORY_MAP_GRAPH))
}

function writeSessions(root: string): void {
  writeSession(root, 'checkout-flow', 'Checkout flow', [generated('stories', 'story_map'), `${STAMP} validate Stories story_map graph-rule verb-noun-format ${STORY_MAP_FILE}:6 no-chat`])
  writeReport(root, 'checkout-flow')
  writeSession(root, 'billing-report', 'Billing report', [])
  writeSession(root, 'move-me', 'Move me', [])
  writeSession(root, 'back-to-backlog', 'Back to backlog', [])
  writeSession(root, 'pricing-rules', 'Pricing rules', [`${STAMP} move Specification no-chat`, generated('stories', 'scenarios'), validated('Stories', 'scenarios')])
  writeSession(root, 'shipped-work', 'Shipped work', [], join('closed', 'shipped-work'))
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

export function createFixtureRepo(root: string): void {
  rmSync(root, { recursive: true, force: true })
  mkdirSync(root, { recursive: true })
  writeInto(join(root, STORY_MAP_FILE), STORY_MAP_TEXT)
  writeInto(join(root, '.gitignore'), '.sessions/\n')
  commitAll(root)
  writeSessions(root)
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) createFixtureRepo(fixtureRoot)
