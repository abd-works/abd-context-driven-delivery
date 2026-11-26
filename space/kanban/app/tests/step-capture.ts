/**
 * The step capture hook for browser story tests: each Given, When and Then runs through `step`, which waits for the
 * page to settle, screenshots it, and writes one row to the run's `results.json` under its story › scenario › step key,
 * the row the walk report (`harness/e2e_review/report/report.ts`) reads.
 *
 * The run folder is `<repo>/.sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>`, the epic and sub-epic taken
 * from the spec's folder under `story_tests/`. `E2E_RELEASE` names the release (default `local`), `E2E_RUN` the run
 * (default the run's start time), and `E2E_RESULTS_ROOT` moves the whole `e2e-test-results` folder.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, join, relative, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

import { test } from '@playwright/test'
import type { Page } from '@playwright/test'

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..')
const STORY_TESTS = join(REPO_ROOT, 'story_tests')
const RESULTS_ROOT = process.env.E2E_RESULTS_ROOT ?? join(REPO_ROOT, '.sessions', process.env.E2E_RELEASE ?? 'local', 'e2e-test-results')
// One run name for the whole Playwright run, so every worker and spec writes into the same run folder.
const RUN = (process.env.E2E_RUN ??= new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-'))
const RESULTS_FILE = 'results.json'

/** The page is photographed once its animations have run and nothing on it has changed for this long. */
const PAGE_QUIET_MS = 300
const PAGE_SETTLE_MAX_MS = 5_000

type StepRow = { key: string; step: string; screenshot: string; by: 'run by a test'; result: 'pass' | 'fail' }

const stepsTaken = new Map<string, number>()

/**
 * Run one Given, When or Then of the current test: `text` is the step as the scenario writes it. After the body, pass
 * or fail, the settled page is photographed and the step's row is written; a failing body still fails the test.
 */
export async function step(page: Page, text: string, body: () => Promise<void> | void): Promise<void> {
  const info = test.info()
  const number = (stepsTaken.get(info.testId) ?? 0) + 1
  stepsTaken.set(info.testId, number)
  const story = info.titlePath[info.titlePath.length - 2] ?? ''
  const key = `${story} › ${info.title} › ${number} ${text}`
  let failure: unknown
  await test.step(text, async () => {
    try {
      await body()
    } catch (error) {
      failure = error
    }
  })
  await capture(page, info.file, key, text, failure === undefined ? 'pass' : 'fail')
  if (failure !== undefined) throw failure
}

async function capture(page: Page, specFile: string, key: string, text: string, result: 'pass' | 'fail'): Promise<void> {
  const runDir = runFolderOf(specFile)
  const screenshot = `screens/${slug(key)}.png`
  mkdirSync(join(runDir, 'screens'), { recursive: true })
  await settle(page)
  await page.screenshot({ path: join(runDir, screenshot) }).catch(() => undefined)
  writeRow(runDir, { key, step: text, screenshot, by: 'run by a test', result })
}

/** `<results>/<epic>/<sub-epic>/<run>` for a spec in `story_tests/<epic>/<sub-epic>/`. */
function runFolderOf(specFile: string): string {
  const [epic = 'other', subEpic = 'other'] = relative(STORY_TESTS, dirname(specFile)).split(sep)
  return join(RESULTS_ROOT, epic, subEpic, RUN)
}

/** A step run again (a retry) replaces its earlier row, so the file holds one row per step. */
function writeRow(runDir: string, row: StepRow): void {
  const file = join(runDir, RESULTS_FILE)
  const rows: StepRow[] = existsSync(file) ? JSON.parse(readFileSync(file, 'utf-8')) : []
  writeFileSync(file, `${JSON.stringify([...rows.filter(earlier => earlier.key !== row.key), row], null, 2)}\n`)
}

/** Fonts loaded, finite animations finished, and no change on the page for PAGE_QUIET_MS (as pml-web's settlePage). */
async function settle(page: Page): Promise<void> {
  await page.evaluate(async ({ quietMs, maxMs }) => {
    const giveUp = new Promise<void>(resolve => setTimeout(resolve, maxMs))
    await document.fonts.ready
    const finite = document.getAnimations().filter(animation => animation.effect?.getComputedTiming().iterations !== Infinity)
    await Promise.race([Promise.all(finite.map(animation => animation.finished.catch(() => undefined))), giveUp])
    await new Promise<void>(resolve => {
      const stop = () => { observer.disconnect(); clearTimeout(quiet); clearTimeout(hardStop); resolve() }
      let quiet = setTimeout(stop, quietMs)
      const hardStop = setTimeout(stop, maxMs)
      const observer = new MutationObserver(() => { clearTimeout(quiet); quiet = setTimeout(stop, quietMs) })
      observer.observe(document.body, { subtree: true, childList: true, attributes: true, characterData: true })
    })
  }, { quietMs: PAGE_QUIET_MS, maxMs: PAGE_SETTLE_MAX_MS }).catch(() => undefined)
}

function slug(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 120)
}
