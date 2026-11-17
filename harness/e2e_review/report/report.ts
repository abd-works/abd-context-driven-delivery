/**
 * Walk report: one self-contained `report.html` per run folder, built from the run's `results.json` and screenshots.
 * Each step shows its Given/When/Then text, its one screenshot, and the agent's verdict with its reason.
 *
 * Copied from pml-web's `test-utils/legacy-compare/report.ts` and reduced to one run: no second system, no check kinds.
 * `npx tsx harness/e2e_review/report/report.ts .sessions/<release>/e2e-test-results/<epic>/<sub-epic>/<run>` rebuilds it.
 */

import { appendFileSync, existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { PNG } from 'pngjs';

export const RESULTS_FILE = 'results.json';
export const REPORT_FILE = 'report.html';

export type Verdict = 'meets the intent' | 'misses the intent';
export type StepResult = 'pass' | 'fail';

/** One step of a run, as the walk recorder or the step capture hook writes it. */
export type StepRow = {
  /** `Story › Scenario › <number> <step text>` */
  key: string;
  /** The step's Given, When or Then text. */
  step: string;
  /** The screenshot, relative to the run folder. */
  screenshot: string;
  by: 'walked by hand' | 'run by a test';
  /** A test's result; a walk by hand has none. */
  result?: StepResult;
  verdict?: Verdict;
  reason?: string;
};

type Step = StepRow & { title: string; number: number };
type Scenario = { story: string; scenario: string; steps: Step[] };
type Tally = { meets: number; misses: number; unjudged: number; failed: number };

const ASSETS_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), 'assets');

/** Write `<runDir>/report.html` and return its path. */
export function writeWalkReport(runDir: string): string {
  const file = path.join(runDir, REPORT_FILE);
  writeFileSync(file, renderPage(runDir, groupScenarios(readRows(runDir))));
  return file;
}

/**
 * Write the run's no-image report into the run history, `<historyDir>/<run>.html` (`<run>` is `<epic>/<sub-epic>`), and
 * add the run's counts and missed steps to `<historyDir>/summary.md`. Return the page's path. The history is never cleared.
 */
export function writeHistoryReport(runDir: string, historyDir: string, run: string): string {
  const scenarios = groupScenarios(readRows(runDir));
  const file = path.join(historyDir, `${run}.html`);
  mkdirSync(path.dirname(file), { recursive: true });
  writeFileSync(file, renderPage(runDir, scenarios, false));
  appendFileSync(path.join(historyDir, 'summary.md'), renderSummaryMarkdown(run, scenarios));
  return file;
}

/**
 * Write `<root>/story-map.html` and return its path: each sub-epic's newest run on one page, linked to that run's own
 * report. `root` is `e2e-test-results`; a run folder is `<epic>/<sub-epic>/<run>` and holds `results.json`.
 */
export function writeStoryMapReport(root: string): string {
  const newest = new Map<string, string>();
  for (const run of runFolders(root)) newest.set(subEpicOf(run), run);
  const groups = new Map<string, Scenario[]>();
  const reportOf = new Map<string, string>();
  for (const [subEpic, run] of [...newest.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    groups.set(subEpic, groupScenarios(readRows(path.join(root, run))));
    reportOf.set(subEpic, `${run}/${REPORT_FILE}`);
  }
  const file = path.join(root, 'story-map.html');
  writeFileSync(file, renderStoryMap(groups, reportOf));
  return file;
}

export const COMPARE_FILE = 'compare.html';

/** How a step's screen stands against the same step of the run it is compared with. */
export type Change = 'same' | 'changed' | 'new' | 'gone';

/** One step of this run beside the same step of the run it is compared with. */
export type StepPair = { key: string; change: Change; changedPercent: number; ours?: StepRow; theirs?: StepRow };

/**
 * A pair changed when at least this many of its 8px blocks moved. pml-web gates on 1% of the page, tuned for two
 * different systems; two runs of the same system match block for block (Maintain Tickets: 58 of 61 pairs moved no
 * block), and a red failure toast on a 1600×1600 page is only 0.93% of it, so a share of the page hides small changes.
 */
const LOOK_GATE_BLOCKS = 4;
const LOOK_BLOCK_PX = 8;
const LOOK_BLOCK_LIMIT = 6;

/**
 * Pair each step of `runDir` with the same step of `againstDir` (an accepted walk, or the last accepted run) and say
 * whether its screen changed, by pixels: the share of 8px blocks whose average grey moved by more than 6 levels.
 */
export function stepPairs(runDir: string, againstDir: string): StepPair[] {
  const ours = new Map(readRows(runDir).map(row => [row.key, row]));
  const theirs = new Map(readRows(againstDir).map(row => [row.key, row]));
  const keys = [...new Set([...ours.keys(), ...theirs.keys()])];
  return keys.map(key => {
    const mine = ours.get(key);
    const other = theirs.get(key);
    if (!other) return { key, change: 'new', changedPercent: 100, ours: mine };
    if (!mine) return { key, change: 'gone', changedPercent: 100, theirs: other };
    const look = lookDifference(path.join(againstDir, other.screenshot), path.join(runDir, mine.screenshot));
    return { key, change: look.changedBlocks >= LOOK_GATE_BLOCKS ? 'changed' : 'same', changedPercent: look.changedPercent, ours: mine, theirs: other };
  });
}

/** Write `<runDir>/compare.html`: each step's screen in `againstDir` and in `runDir` side by side, and return its path. */
export function writeCompareReport(runDir: string, againstDir: string): string {
  const file = path.join(runDir, COMPARE_FILE);
  writeFileSync(file, renderComparePage(runDir, againstDir, stepPairs(runDir, againstDir)));
  return file;
}

/** How many 8px blocks' average grey moved, and their share in percent; screens of different sizes count as all changed. */
function lookDifference(theirFile: string, ourFile: string): { changedBlocks: number; changedPercent: number } {
  const everything = { changedBlocks: Number.POSITIVE_INFINITY, changedPercent: 100 };
  if (!existsSync(theirFile) || !existsSync(ourFile)) return everything;
  const one = PNG.sync.read(readFileSync(theirFile));
  const two = PNG.sync.read(readFileSync(ourFile));
  if (one.width !== two.width || one.height !== two.height) return everything;
  let changed = 0;
  let blocks = 0;
  for (let by = 0; by + LOOK_BLOCK_PX <= one.height; by += LOOK_BLOCK_PX) {
    for (let bx = 0; bx + LOOK_BLOCK_PX <= one.width; bx += LOOK_BLOCK_PX) {
      blocks++;
      if (Math.abs(blockGrey(one, bx, by) - blockGrey(two, bx, by)) > LOOK_BLOCK_LIMIT) changed++;
    }
  }
  return { changedBlocks: changed, changedPercent: blocks ? (100 * changed) / blocks : 0 };
}

function blockGrey(image: PNG, left: number, top: number): number {
  let sum = 0;
  for (let y = top; y < top + LOOK_BLOCK_PX; y++) {
    for (let x = left; x < left + LOOK_BLOCK_PX; x++) {
      const at = (y * image.width + x) * 4;
      sum += 0.299 * image.data[at] + 0.587 * image.data[at + 1] + 0.114 * image.data[at + 2];
    }
  }
  return sum / (LOOK_BLOCK_PX * LOOK_BLOCK_PX);
}

function renderComparePage(runDir: string, againstDir: string, pairs: StepPair[]): string {
  const run = path.basename(runDir);
  const against = path.basename(againstDir);
  const subEpic = subEpicOf([path.basename(path.dirname(path.dirname(runDir))), path.basename(path.dirname(runDir)), run].join('/'));
  const shots = new EmbeddedShots(runDir);
  const scenarios = new Map<string, StepPair[]>();
  for (const pair of pairs) {
    const { story, scenario } = keyParts(pair.key);
    const id = `${story} › ${scenario}`;
    scenarios.set(id, [...(scenarios.get(id) ?? []), pair]);
  }
  const reviewFile = path.join(runDir, 'review.json');
  const review = existsSync(reviewFile) ? (JSON.parse(readFileSync(reviewFile, 'utf8')) as { against: string; pairs: Record<string, { verdict: string; reason: string; cites?: string }> }) : undefined;
  const judged = review?.against === against ? review.pairs : {};
  const counts = (list: StepPair[]) => (['same', 'changed', 'new', 'gone'] as Change[]).map(change => `${list.filter(pair => pair.change === change).length} ${change}`).join(' · ');
  const cards = [...scenarios.entries()].map(([id, list]) => {
    list.sort((a, b) => (Number.parseInt(keyParts(a.key).step, 10) || 0) - (Number.parseInt(keyParts(b.key).step, 10) || 0));
    const differs = list.some(pair => pair.change !== 'same');
    const steps = list.map(pair => {
      const row = pair.ours ?? pair.theirs!;
      const chip = `<span class="chip ${pair.change === 'same' ? 'pass' : 'fail'}">${pair.change}${pair.change === 'changed' ? ` ${pair.changedPercent.toFixed(2)}%` : ''}</span>`;
      const judgement = judged[pair.key];
      const verdict = judgement
        ? `<span class="chip ${judgement.verdict === 'intended' ? 'pass' : 'fail'}">${escapeHtml(judgement.verdict)}</span>`
        : pair.change !== 'same' ? '<span class="chip none">not judged</span>' : pair.ours?.verdict ? verdictChip(pair.ours) : '';
      const why = judgement ? `${judgement.reason}${judgement.cites ? ` (${judgement.cites})` : ''}` : pair.ours?.reason ?? '';
      const reason = why ? `<p class="reason">${escapeHtml(why)}</p>` : '';
      const pictures = `<div class="shots">${pair.theirs ? renderShot(shots, pair.theirs.screenshot, againstDir, against) : `<div class="shot missing">${escapeHtml(against)}: no such step</div>`}${pair.ours ? renderShot(shots, pair.ours.screenshot, runDir, run) : `<div class="shot missing">${escapeHtml(run)}: no such step</div>`}</div>`;
      return `<article class="step${pair.change !== 'same' ? ' failing' : ''}"><header><h4>${escapeHtml(keyParts(row.key).step)}</h4><div class="chips">${chip}${verdict}${pair.ours ? resultChip(pair.ours) : ''}</div></header>${reason}${pictures}</article>`;
    });
    return `<details class="scenario${differs ? ' failing' : ''}" id="${anchor(id)}"${differs ? ' open' : ''}><summary><span class="title">${escapeHtml(id)}</span><span class="counts">${counts(list)}</span></summary>${steps.join('')}</details>`;
  });
  return fillTemplate({
    title: escapeHtml(`End-to-end compare — ${subEpic}`),
    run: escapeHtml(`${run} against ${against}`),
    totals: `${counts(pairs)} &nbsp;·&nbsp; ${escapeHtml(run)} against ${escapeHtml(against)} &nbsp;·&nbsp; written ${new Date().toISOString().slice(0, 16).replace('T', ' ')} UTC`,
    logo: logoImages(),
    summary: '',
    sections: `<section class="sub-epic-section" id="${anchor(subEpic)}">${sectionLabel(1, subEpic)}${cards.join('')}</section>`,
    shotLoader: SHOT_LOADER.replace('{{shots}}', () => shots.json()),
  });
}

/** One run's section of the history summary: counts per story, then every missed or failed step as text. */
function renderSummaryMarkdown(run: string, scenarios: Scenario[]): string {
  const all = tally(scenarios.flatMap(scenario => scenario.steps));
  const lines = [`## ${run} — ${all.meets} meet · ${all.misses} miss · ${all.unjudged} not judged · ${all.failed} failed`, '', '| Story | meet | miss | not judged | failed |', '|---|---|---|---|---|'];
  for (const story of storiesOf(scenarios)) {
    const counts = tally(stepsOfStory(scenarios, story));
    lines.push(`| ${story} | ${counts.meets} | ${counts.misses} | ${counts.unjudged} | ${counts.failed} |`);
  }
  const missed = scenarios.flatMap(scenario => scenario.steps).filter(isFailing);
  lines.push('', missed.length ? '### Missed or failed steps' : 'No missed or failed steps.', '');
  for (const step of missed) lines.push(`- ${step.key} — ${step.verdict ?? 'not judged'}${step.result === 'fail' ? ', test failed' : ''} — ${(step.reason ?? '').replace(/\s+/g, ' ')}`);
  return `${lines.join('\n')}\n\n`;
}

/** The run folders under `root`, `<epic>/<sub-epic>/<run>` as forward-slash paths, oldest name first. */
function runFolders(root: string, under = ''): string[] {
  const dir = path.join(root, under);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter(entry => statSync(path.join(dir, entry)).isDirectory())
    .map(entry => (under ? `${under}/${entry}` : entry))
    .flatMap(folder => (existsSync(path.join(root, folder, RESULTS_FILE)) ? [folder] : runFolders(root, folder)))
    .sort();
}

/** `Epic › Sub-epic` from a run's `<epic>/<sub-epic>/<run>` folder. */
function subEpicOf(run: string): string {
  const parts = run.split('/').slice(0, -1);
  return parts.length ? parts.map(titleCase).join(' › ') : 'Other stories';
}

function readRows(runDir: string): StepRow[] {
  const file = path.join(runDir, RESULTS_FILE);
  if (!existsSync(file)) return [];
  return JSON.parse(readFileSync(file, 'utf8')) as StepRow[];
}

function keyParts(key: string): { story: string; scenario: string; step: string } {
  const [story = key, scenario = '', ...step] = key.split(' › ');
  return { story, scenario, step: step.join(' › ') };
}

function groupScenarios(rows: StepRow[]): Scenario[] {
  const scenarios = new Map<string, Scenario>();
  for (const row of rows) {
    const parts = keyParts(row.key);
    const id = `${parts.story} › ${parts.scenario}`;
    if (!scenarios.has(id)) scenarios.set(id, { story: parts.story, scenario: parts.scenario, steps: [] });
    scenarios.get(id)!.steps.push({ ...row, title: parts.step, number: Number.parseInt(parts.step, 10) || 0 });
  }
  for (const scenario of scenarios.values()) scenario.steps.sort((a, b) => a.number - b.number);
  return [...scenarios.values()];
}

function storiesOf(scenarios: Scenario[]): string[] {
  return [...new Set(scenarios.map(scenario => scenario.story))];
}

function stepsOfStory(scenarios: Scenario[], story: string): Step[] {
  return scenarios.filter(scenario => scenario.story === story).flatMap(scenario => scenario.steps);
}

function isFailing(step: StepRow): boolean {
  return step.verdict === 'misses the intent' || step.result === 'fail';
}

function tally(steps: StepRow[]): Tally {
  return {
    meets: steps.filter(step => step.verdict === 'meets the intent').length,
    misses: steps.filter(step => step.verdict === 'misses the intent').length,
    unjudged: steps.filter(step => !step.verdict).length,
    failed: steps.filter(step => step.result === 'fail').length,
  };
}

function titleCase(slugText: string): string {
  return slugText.replace(/[-_]/g, ' ').replace(/(^|\s)\S/g, letter => letter.toUpperCase());
}

function escapeHtml(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function anchor(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function verdictChip(step: StepRow): string {
  if (!step.verdict) return '<span class="chip none">not judged</span>';
  return `<span class="chip ${step.verdict === 'meets the intent' ? 'pass' : 'fail'}">${step.verdict}</span>`;
}

function resultChip(step: StepRow): string {
  if (!step.result) return '';
  return `<span class="chip ${step.result}">test ${step.result === 'pass' ? 'passed' : 'failed'}</span>`;
}

/**
 * The step screenshots, embedded in the page: a viewer that opens `report.html` on its own (Claude's file pane)
 * cannot reach the run folder. Each distinct screenshot is stored once, at half size; the link still opens the
 * full-size file when the page is opened from the run folder.
 */
class EmbeddedShots {
  private readonly idByHash = new Map<string, string>();
  private readonly dataById = new Map<string, string>();

  constructor(readonly runDir: string, readonly withImages = true) {}

  has(file: string, from = this.runDir): boolean {
    return file !== '' && existsSync(path.join(from, file));
  }

  embed(file: string, from = this.runDir): string {
    const bytes = readFileSync(path.join(from, file));
    const hash = createHash('sha1').update(bytes).digest('hex');
    const known = this.idByHash.get(hash);
    if (known) return known;
    const id = `s${this.idByHash.size}`;
    this.idByHash.set(hash, id);
    this.dataById.set(id, PNG.sync.write(halfSize(PNG.sync.read(bytes)), { colorType: 2, deflateLevel: 9 }).toString('base64'));
    return id;
  }

  json(): string {
    return JSON.stringify(Object.fromEntries(this.dataById));
  }
}

/** Average each 2×2 block of pixels, on a white background. */
function halfSize(image: PNG): PNG {
  const width = Math.max(1, image.width >> 1);
  const height = Math.max(1, image.height >> 1);
  const half = new PNG({ width, height });
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const corners = [[0, 0], [1, 0], [0, 1], [1, 1]].map(([dx, dy]) => (Math.min(y * 2 + dy, image.height - 1) * image.width + Math.min(x * 2 + dx, image.width - 1)) * 4);
      for (let channel = 0; channel < 3; channel++) {
        const sum = corners.reduce((total, at) => total + (image.data[at + channel] * image.data[at + 3] + 255 * (255 - image.data[at + 3])) / 255, 0);
        half.data[(y * width + x) * 4 + channel] = Math.round(sum / 4);
      }
      half.data[(y * width + x) * 4 + 3] = 255;
    }
  }
  return half;
}

/** `from` is the run folder holding the file; a caption names the run when two are shown side by side. */
function renderShot(shots: EmbeddedShots, file: string, from = shots.runDir, caption = ''): string {
  if (!shots.withImages) return '';
  const label = caption ? `<figcaption>${escapeHtml(caption)}</figcaption>` : '';
  if (!shots.has(file, from)) return `<div class="shot missing">${caption ? `${escapeHtml(caption)}: ` : ''}no screenshot</div>`;
  const src = [path.relative(shots.runDir, from).split(path.sep).join('/'), file].filter(Boolean).join('/').split('/').map(encodeURIComponent).join('/');
  return `<figure class="shot"><a href="${src}" target="_blank" rel="noopener"><img data-shot="${shots.embed(file, from)}" alt="step screenshot"></a>${label}</figure>`;
}

function renderStep(step: Step, shots: EmbeddedShots): string {
  const reason = step.reason ? `<p class="reason">${escapeHtml(step.reason)}</p>` : '';
  return `<article class="step${isFailing(step) ? ' failing' : ''}"><header><h4>${escapeHtml(step.title)}</h4><div class="chips">${verdictChip(step)}${resultChip(step)}</div></header>${reason}${renderShot(shots, step.screenshot)}</article>`;
}

function renderScenario(scenario: Scenario, shots: EmbeddedShots): string {
  const counts = tally(scenario.steps);
  const failing = scenario.steps.some(isFailing);
  const id = anchor(`${scenario.story} ${scenario.scenario}`);
  return `<details class="scenario${failing ? ' failing' : ''}" id="${id}"${failing ? ' open' : ''}><summary><span class="title">${escapeHtml(scenario.story)} › ${escapeHtml(scenario.scenario)}</span><span class="counts">${countsText(counts)}</span></summary>${scenario.steps.map(step => renderStep(step, shots)).join('')}</details>`;
}

function countsText(counts: Tally): string {
  const parts = [`${counts.meets} meet`, counts.misses ? `<span class="n-fail">${counts.misses}</span> miss` : '0 miss'];
  if (counts.unjudged) parts.push(`${counts.unjudged} not judged`);
  if (counts.failed) parts.push(`<span class="n-fail">${counts.failed}</span> test failed`);
  return parts.join(' · ');
}

/** The abd.works section label: number, mono name with the cursor, and a rule. */
function sectionLabel(position: number, name: string): string {
  return `<div class="s-label"><span class="s-num">${String(position).padStart(2, '0')}</span><h2 class="s-name">${escapeHtml(name)}</h2><span class="s-rule"></span></div>`;
}

function countCell(count: number, isBad: boolean): string {
  return `<td class="num">${count && isBad ? `<span class="n-fail">${count}</span>` : count}</td>`;
}

/** `reportOf` points each sub-epic at the page that shows its scenarios; without it they are on this page. */
function renderSummary(groups: Map<string, Scenario[]>, reportOf = new Map<string, string>()): string {
  const body = [...groups.entries()]
    .map(([subEpic, scenarios]) => {
      const page = reportOf.get(subEpic) ?? '';
      const storyRows = storiesOf(scenarios).map(story => {
        const counts = tally(stepsOfStory(scenarios, story));
        const first = scenarios.find(scenario => scenario.story === story)!;
        return `<tr class="${counts.misses + counts.failed ? 'failing' : ''}"><td class="story"><a href="${page}#${anchor(`${first.story} ${first.scenario}`)}">${escapeHtml(story)}</a></td>${countCell(counts.meets, false)}${countCell(counts.misses, true)}${countCell(counts.unjudged, false)}${countCell(counts.failed, true)}</tr>`;
      });
      const all = tally(scenarios.flatMap(scenario => scenario.steps));
      return `<tr class="sub-epic"><th colspan="5"><a href="${page}#${anchor(subEpic)}">${escapeHtml(subEpic)}</a> <span class="muted">${all.meets} meet · ${all.misses} miss</span></th></tr>${storyRows.join('')}`;
    })
    .join('');
  return `<section>${sectionLabel(1, 'Summary')}<p class="muted small">Each step's screen judged against its Given, When or Then: steps that meet the intent, steps that miss it, steps not judged yet, and steps whose test failed.</p><div class="table-wrap"><table><thead><tr><th>Story</th><th class="num">meet</th><th class="num">miss</th><th class="num">not judged</th><th class="num">test failed</th></tr></thead><tbody>${body}</tbody></table></div></section>`;
}

/** The abd.works wordmark (copied from abd-works-brand/logo), inlined so the page stays one file. */
function wordmark(colour: 'black' | 'white'): string {
  const svg = readFileSync(path.join(ASSETS_DIR, `abd.works.wordmark.${colour}.svg`));
  return `data:image/svg+xml;base64,${svg.toString('base64')}`;
}

/** `withImages` false: the same report with no screenshot or logo image, for the run history. */
function renderPage(runDir: string, scenarios: Scenario[], withImages = true): string {
  const run = path.basename(runDir);
  const subEpic = subEpicOf([path.basename(path.dirname(path.dirname(runDir))), path.basename(path.dirname(runDir)), run].join('/'));
  const shots = new EmbeddedShots(runDir, withImages);
  const all = tally(scenarios.flatMap(scenario => scenario.steps));
  const groups = new Map([[subEpic, scenarios]]);
  const slots: Record<string, string> = {
    title: escapeHtml(`End-to-end walk — ${subEpic}`),
    run: escapeHtml(run),
    totals: `${all.meets} meet · ${all.misses} miss · ${all.unjudged} not judged · ${all.failed} test failed &nbsp;·&nbsp; written ${new Date().toISOString().slice(0, 16).replace('T', ' ')} UTC`,
    logo: withImages ? logoImages() : TEXT_LOGO,
    summary: renderSummary(groups),
    sections: `<section class="sub-epic-section" id="${anchor(subEpic)}">${sectionLabel(2, subEpic)}${scenarios.map(scenario => renderScenario(scenario, shots)).join('')}</section>`,
    shotLoader: withImages ? SHOT_LOADER.replace('{{shots}}', () => shots.json()) : '',
  };
  return fillTemplate(slots);
}

const TEXT_LOGO = '<span class="logo-text">abd.works</span>';

function logoImages(): string {
  return `<img class="logo-light" src="${wordmark('black')}" alt="abd.works"><img class="logo-dark" src="${wordmark('white')}" alt="abd.works">`;
}

/** Fills each screenshot from the page's own embedded data, so the page stands alone. */
const SHOT_LOADER = `<script type="application/json" id="shots">{{shots}}</script>
<script>
(function () {
  var embedded = JSON.parse(document.getElementById('shots').textContent);
  document.querySelectorAll('img[data-shot]').forEach(function (img) {
    var data = embedded[img.getAttribute('data-shot')];
    if (data) img.src = 'data:image/png;base64,' + data;
  });
})();
</script>`;

function renderStoryMap(groups: Map<string, Scenario[]>, reportOf: Map<string, string>): string {
  const all = tally([...groups.values()].flat().flatMap(scenario => scenario.steps));
  return fillTemplate({
    title: 'End-to-end story map',
    run: 'story map',
    totals: `${all.meets} meet · ${all.misses} miss · ${all.unjudged} not judged · ${all.failed} test failed &nbsp;·&nbsp; written ${new Date().toISOString().slice(0, 16).replace('T', ' ')} UTC`,
    logo: logoImages(),
    summary: renderSummary(groups, reportOf),
    shotLoader: '',
  });
}

function fillTemplate(slots: Record<string, string>): string {
  // A function replacer, so `$` in page text ("$70.00") is never read as a replacement pattern.
  return PAGE_TEMPLATE.replace(/\{\{(\w+)\}\}/g, (_, slot: string) => slots[slot] ?? '');
}

const PAGE_TEMPLATE = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{title}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<script>try { if (localStorage.getItem('abd-mode') === 'engineering') document.documentElement.setAttribute('data-theme', 'engineering'); } catch (e) {}</script>
<style>
/* abd.works brand tokens (abd-works-brand/css/brand.css), inlined so the report stays one file. */
:root {
  --bg: #F6F5F3; --surface: #FFFFFF; --raised: #F0ECE4; --faint: #EFECE6; --border: #DDD8CF; --border-sub: #E7E1D6;
  --text: #111113; --muted: #595A61;
  --accent: #E5531A; --accent-deep: #C64514; --accent-soft: #F2A07A; --accent-dim: rgba(229,83,26,0.10); --accent-dim2: rgba(229,83,26,0.18);
  --success: #22C55E; --warning: #F59E0B; --error: #EF4444;
  --font-sans: 'Inter', system-ui, sans-serif; --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --max-width: 1280px;
  --text-xs: clamp(10px, 1.2vw, 11px); --text-sm: clamp(12px, 1.4vw, 13px); --text-base: clamp(14px, 1.7vw, 15px);
  --text-md: clamp(16px, 2vw, 18px); --text-lg: clamp(20px, 2.5vw, 26px); --text-xl: clamp(28px, 3.8vw, 34px);
  --radius-sm: 4px; --radius-card: 6px; --radius-pill: 999px;
  --space-2xs: 4px; --space-xs: 8px; --space-sm: 12px; --space-md: 16px; --space-lg: 24px; --space-xl: 32px; --space-2xl: 48px;
}
html[data-theme="engineering"] {
  --bg: #0B0B0B; --surface: #111113; --raised: #1B1B20; --faint: #1A1A1E; --border: #2A2A2A; --border-sub: #1A1A1E;
  --text: #E8E8ED; --muted: #9B9BA8;
}
*, ::before, ::after { box-sizing: border-box; margin: 0; padding: 0; }
html { background: var(--bg); color: var(--text); font-family: var(--font-sans); font-size: 15px; line-height: 1.65; -webkit-font-smoothing: antialiased; color-scheme: light; }
html[data-theme="engineering"] { color-scheme: dark; }
body { background: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
a { color: var(--accent); text-decoration: none; transition: color 120ms ease; }
a:hover { color: var(--accent-deep); }
a:focus-visible, button:focus-visible, input:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.muted { color: var(--muted); }
.small { font-size: var(--text-sm); }

/* —— Site nav (brand shell) —— */
.site-nav { position: sticky; top: 0; z-index: 110; background: rgba(246,245,243,0.92); backdrop-filter: blur(16px) saturate(180%); -webkit-backdrop-filter: blur(16px) saturate(180%); border-bottom: 1px solid var(--border); padding: 12px 48px; display: grid; gap: 10px; }
html[data-theme="engineering"] .site-nav { background: rgba(11,11,11,0.92); }
.nav-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.nav-logo { display: inline-flex; align-items: center; flex-shrink: 0; }
.nav-logo img { display: block; height: clamp(28px, 3.2vw, 40px); width: auto; }
.logo-text { font: 700 22px/1 var(--font-heading, inherit); letter-spacing: -0.02em; }
html:not([data-theme="engineering"]) .logo-dark, html[data-theme="engineering"] .logo-light { display: none !important; }
.nav-title { font-family: var(--font-mono); font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin-right: auto; padding-left: 16px; border-left: 1px solid var(--border); }
.filters { display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: center; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--muted); }
.filters label { display: inline-flex; gap: 5px; align-items: center; white-space: nowrap; cursor: pointer; }
.filters input { accent-color: var(--accent); }
.filters .primary { color: var(--text); font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.btn-ghost { font-family: var(--font-mono); font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding: 4px 10px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: transparent; color: var(--text); cursor: pointer; transition: border-color 120ms ease; }
.btn-ghost:hover { border-color: var(--accent); }

/* —— Mode toggle (brand) —— */
.mode-switch { display: inline-flex; align-items: center; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-pill); padding: 2px; gap: 2px; }
.mode-btn { border: none; border-radius: var(--radius-pill); background: transparent; color: var(--muted); font-family: var(--font-mono); font-size: var(--text-xs); font-weight: 500; line-height: 1; padding: 6px 9px; cursor: pointer; white-space: nowrap; transition: background-color 120ms ease, color 120ms ease; }
.mode-btn:hover { color: var(--text); }
.mode-btn.is-active { background: var(--accent); color: #0B0B0B; }

/* —— Layout —— */
main { flex: 1; width: 100%; max-width: var(--max-width); margin: 0 auto; padding: var(--space-xl) 48px var(--space-2xl); display: grid; gap: var(--space-xl); }
.page-head { display: grid; gap: var(--space-xs); }
.kicker { font-family: var(--font-mono); font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); }
.kicker::after { content: '_'; font-weight: 700; margin-left: 2px; animation: cursor-blink 1.1s step-end infinite; }
h1 { font-size: var(--text-xl); font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; }
.meta { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--muted); }

/* —— Section labels (brand) —— */
section { display: grid; gap: var(--space-sm); min-width: 0; }
.s-label { display: flex; align-items: center; gap: 16px; margin-bottom: var(--space-xs); }
.s-num { font-family: var(--font-mono); font-size: var(--text-xs); font-weight: 600; color: var(--muted); letter-spacing: 0.08em; }
.s-name { font-family: var(--font-mono); font-size: var(--text-sm); font-weight: 600; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.s-name::after { content: '_'; font-weight: 700; color: var(--accent); margin-left: 1px; animation: cursor-blink 1.1s step-end infinite; }
.s-rule { flex: 1; height: 1px; background: var(--border); min-width: 24px; }
@keyframes cursor-blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* —— Chips —— */
.chip { display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-mono); font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; padding: 3px 9px; border-radius: var(--radius-pill); border: 1px solid var(--border); background: var(--surface); color: var(--text); white-space: nowrap; }
.chip::before { content: ''; width: 7px; height: 7px; border-radius: 50%; background: var(--muted); }
.chip.pass::before { background: var(--success); }
.chip.fail { border-color: var(--error); }
.chip.fail::before { background: var(--error); }
.chip.none { color: var(--muted); }
.n-fail { color: var(--text); font-weight: 700; }
.n-fail::before { content: '● '; color: var(--error); font-size: 0.8em; }

/* —— Table (brand) —— */
.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: var(--text-sm); font-variant-numeric: tabular-nums; }
th, td { padding: 8px 12px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }
thead th { background: var(--raised); font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
tr:last-child td { border-bottom: 0; }
.num { text-align: right; white-space: nowrap; }
tr.sub-epic th { background: var(--faint); font-family: var(--font-mono); font-size: var(--text-xs); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; padding-top: 10px; }
tr.sub-epic th a { color: var(--text); }
td.story { padding-left: 24px; }
tbody tr:not(.sub-epic):hover td { background: var(--accent-dim); }

/* —— Scenario cards (brand: surface, 1px border, 6px radius, no shadow) —— */
.sub-epic-section { gap: var(--space-xs); }
details.scenario { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-card); overflow: hidden; transition: border-color 150ms ease; }
details.scenario:hover { border-color: var(--accent-soft); }
details.scenario.failing { box-shadow: inset 3px 0 0 var(--error); }
details.scenario > summary { cursor: pointer; padding: 12px 16px; display: flex; flex-wrap: wrap; gap: 4px 16px; justify-content: space-between; align-items: baseline; list-style: none; }
details.scenario > summary::-webkit-details-marker { display: none; }
details.scenario > summary .title { font-weight: 600; }
details.scenario > summary .title::before { content: '›'; display: inline-block; margin-right: 8px; color: var(--accent); font-weight: 700; transition: transform 150ms ease; }
details.scenario[open] > summary .title::before { transform: rotate(90deg); }
details.scenario > summary .counts { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--muted); }

/* —— Steps —— */
.step { border-top: 1px solid var(--border); padding: 14px 16px; display: grid; gap: 12px; min-width: 0; }
.step.failing { box-shadow: inset 3px 0 0 var(--error); background: var(--faint); }
.step > header { display: flex; flex-wrap: wrap; gap: 6px 12px; justify-content: space-between; align-items: baseline; }
.step h4 { font-family: var(--font-mono); font-size: var(--text-sm); font-weight: 600; overflow-wrap: anywhere; }
.chips { display: flex; gap: 6px; }
.reason { font-size: var(--text-sm); color: var(--muted); overflow-wrap: anywhere; }
.shot { min-width: 0; max-width: 720px; }
.shots { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.shots .shot { max-width: none; }
.shot figcaption { font-family: var(--font-mono); font-size: var(--text-xs); letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); margin-top: 4px; }
.shot img { display: block; width: 100%; border: 1px solid var(--border); border-radius: var(--radius-sm); background: #fff; transition: border-color 150ms ease; }
.shot a:hover img { border-color: var(--accent); }
.shot.missing { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--muted); padding: 12px; border: 1px dashed var(--border); border-radius: var(--radius-sm); }

/* —— Footer (brand) —— */
.site-footer { border-top: 1px solid var(--border); padding: 24px 48px; display: flex; align-items: center; gap: 16px; }
.site-footer img { display: block; height: 20px; width: auto; opacity: 0.6; }
.footer-tagline { font-size: var(--text-sm); color: var(--muted); font-style: italic; }

/* —— Filter —— */
body.missed-only details.scenario:not(.failing),
body.missed-only .step:not(.failing),
body.missed-only tbody tr:not(.failing):not(.sub-epic) { display: none; }

@media (max-width: 900px) {
  .site-nav, main, .site-footer { padding-left: 16px; padding-right: 16px; }
  .nav-title { display: none; }
}
@media (prefers-reduced-motion: reduce) { .s-name::after, .kicker::after { animation: none; } }
</style>
</head>
<body>
<nav class="site-nav" aria-label="Report">
  <div class="nav-row">
    <span class="nav-logo">{{logo}}</span>
    <span class="nav-title">End-to-end walk · {{run}}</span>
    <div class="mode-switch" role="group" aria-label="Display mode">
      <button class="mode-btn is-active" type="button" data-mode="executive" aria-pressed="true">Executive</button>
      <button class="mode-btn" type="button" data-mode="engineering" aria-pressed="false">Engineering</button>
    </div>
  </div>
  <div class="filters">
    <label class="primary"><input type="checkbox" id="missed-only"> Missed or changed only</label>
    <button type="button" class="btn-ghost" id="open-all">Open all</button>
    <button type="button" class="btn-ghost" id="close-all">Close all</button>
  </div>
</nav>
<main>
  <header class="page-head">
    <p class="kicker">Screens against their steps</p>
    <h1>{{title}}</h1>
    <p class="meta">{{totals}}</p>
    <p class="muted small">Each step's screen is judged against its Given, When or Then: the Given's state is visible, the When took effect, the Then shows the right values, labels and messages.</p>
  </header>
  {{summary}}
  {{sections}}
</main>
<footer class="site-footer">
  {{logo}}
  <p class="footer-tagline">Tools don't transform companies. People do.</p>
</footer>
{{shotLoader}}
<script>
(function () {
  var root = document.documentElement;
  var body = document.body;
  var modeButtons = Array.prototype.slice.call(document.querySelectorAll('.mode-btn'));
  function setMode(mode, persist) {
    if (mode === 'engineering') root.setAttribute('data-theme', 'engineering'); else root.removeAttribute('data-theme');
    modeButtons.forEach(function (b) { var on = b.dataset.mode === mode; b.classList.toggle('is-active', on); b.setAttribute('aria-pressed', String(on)); });
    if (persist) { try { localStorage.setItem('abd-mode', mode); } catch (e) {} }
  }
  modeButtons.forEach(function (b) { b.addEventListener('click', function () { setMode(b.dataset.mode, true); }); });
  setMode(root.getAttribute('data-theme') === 'engineering' ? 'engineering' : 'executive', false);

  var missedOnly = document.getElementById('missed-only');
  missedOnly.addEventListener('change', function () { body.classList.toggle('missed-only', missedOnly.checked); });
  function openAll(open) { document.querySelectorAll('details.scenario').forEach(function (d) { d.open = open; }); }
  document.getElementById('open-all').addEventListener('click', function () { openAll(true); });
  document.getElementById('close-all').addEventListener('click', function () { openAll(false); });
  function openTarget(id) { var target = document.getElementById(id); if (target && target.tagName === 'DETAILS') target.open = true; }
  if (location.hash) openTarget(location.hash.slice(1));
  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href^="#"]');
    if (link) openTarget(link.getAttribute('href').slice(1));
  });
})();
</script>
</body>
</html>
`;

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  const againstAt = args.indexOf('--against');
  const against = againstAt >= 0 ? args.splice(againstAt, 2)[1] : '';
  const runDirs = args;
  if (!runDirs.length) {
    console.error('Usage: npx tsx harness/e2e_review/report/report.ts <run folder> [more runs] [--against <accepted run folder>]');
    process.exit(1);
  }
  for (const runDir of runDirs) {
    if (against) console.log(`Compare report: ${writeCompareReport(path.resolve(runDir), path.resolve(against))}`);
    const resolved = path.resolve(runDir);
    console.log(`Walk report: ${writeWalkReport(resolved)}`);
    console.log(`Story map: ${writeStoryMapReport(path.resolve(resolved, '..', '..', '..'))}`);
  }
}
