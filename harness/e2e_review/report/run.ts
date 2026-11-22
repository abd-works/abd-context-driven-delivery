/**
 * One model of an end-to-end run, read once: a sub-epic's runs and the one it accepted (*SubEpicRuns*), and one run's
 * steps, its regression review, the run it is compared with, its pairs against another run, its verdicts, and its
 * summary (*Run*). The command line (`review.ts`) and the pages (`report.ts`) both read runs through here, and Python
 * reads a run's summary, which every command that changes a run writes beside it.
 *
 * A sub-epic's folder (`<epic>/<sub-epic>/`) holds its runs and `baseline.json`, naming the accepted run. A run's folder
 * holds `results.json`, one row per step; `screens/`, its screenshots; `review.json`, its verdict on each changed pair;
 * and `changed.json`, its summary.
 */

import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { PNG } from 'pngjs';

export const RESULTS_FILE = 'results.json';
export const BASELINE_FILE = 'baseline.json';
export const REVIEW_FILE = 'review.json';
/** The run's summary, kept beside it so the server health report reads it without starting Node. */
export const SUMMARY_FILE = 'changed.json';

export type Verdict = 'meets the intent' | 'misses the intent';
export type StepResult = 'pass' | 'fail';
export type ReviewVerdict = 'intended' | 'regression caught' | 'missed by the tests' | 'noise';

/** Where a screen changed: the box round its changed blocks, each edge a share of the screen from 0 to 1. */
export type Area = { left: number; top: number; width: number; height: number };

/** How a step's screen stands against the same step of the run it is compared with. */
export type Change = 'same' | 'changed' | 'new' | 'gone';

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
  /** Shown, never stored: the earlier run whose judge pass this step's verdict is carried from, its screen unchanged. */
  judgedIn?: string;
  /** Shown, never stored: how the step's screen stands against the same step of the previous run. */
  change?: Change;
  /** Shown, never stored: the previous run it is compared with. */
  previous?: string;
  /** Shown, never stored: the same step's screenshot in the previous run, relative to that run's folder. */
  previousShot?: string;
  /** Shown, never stored: how much of the screen changed since the previous run, in percent, and where. */
  changedPercent?: number;
  changedArea?: Area;
  /** Shown, never stored: the regression review's verdict and reason on the change, when it has one. */
  changeReview?: string;
};

/** One step of a run beside the same step of the run it is compared with. */
export type StepPair = { key: string; change: Change; changedPercent: number; changedArea?: Area; ours?: StepRow; theirs?: StepRow };

/** One changed pair's verdict. `cites` is the story or code change an intended pair follows from, or the failing test. */
export type PairReview = { verdict: ReviewVerdict; reason: string; cites?: string };

export type Review = { against: string; pairs: Record<string, PairReview> };

/** What Python reads of a run: its step count, the steps whose screen changed, those not judged, and those missed. */
export type RunSummary = { steps: number; changed_steps: string[]; unjudged_steps: string[]; missed_steps: string[] };

export class ReviewRefused extends Error {}

/**
 * A pair changed when at least this many of its 8px blocks moved. pml-web gates on 1% of the page, tuned for two
 * different systems; two runs of the same system match block for block (Maintain Tickets: 58 of 61 pairs moved no
 * block), and a red failure toast on a 1600×1600 page is only 0.93% of it, so a share of the page hides small changes.
 */
const LOOK_GATE_BLOCKS = 4;
const LOOK_BLOCK_PX = 8;
const LOOK_BLOCK_LIMIT = 6;
const JUDGE_VERDICTS: Verdict[] = ['meets the intent', 'misses the intent'];

/** A sub-epic's runs: its folder, the run it accepted, and its runs by name. */
export class SubEpicRuns {
  constructor(readonly dir: string) {}

  /** The run the sub-epic's next run is compared with: the last one the person accepted, or none yet. */
  get baseline(): Run | undefined {
    const file = path.join(this.dir, BASELINE_FILE);
    if (!existsSync(file)) return undefined;
    const accepted = new Run(path.join(this.dir, (JSON.parse(readFileSync(file, 'utf8')) as { run: string }).run));
    return accepted.isThere ? accepted : undefined;
  }

  /** The sub-epic's runs, oldest name first. */
  get runs(): Run[] {
    if (!existsSync(this.dir)) return [];
    return readdirSync(this.dir)
      .filter(entry => statSync(path.join(this.dir, entry)).isDirectory())
      .sort()
      .map(entry => new Run(path.join(this.dir, entry)))
      .filter(run => run.isThere);
  }

  /**
   * The person accepts `run`: it becomes the sub-epic's baseline. Refused while a changed pair is unjudged or judged
   * anything but intended, because only an explained change may move the baseline. The first run, with nothing to
   * compare with, is accepted as it is.
   */
  accept(run: Run, acceptedBy: string): string {
    const against = this.baseline;
    if (against && path.resolve(against.dir) !== path.resolve(run.dir)) {
      const open = run.openPairs(against);
      if (open.length) throw new ReviewRefused(`${run.name} has ${open.length} changed step(s) not judged intended: ${open.join('; ')}`);
    }
    writeFileSync(path.join(this.dir, BASELINE_FILE), `${JSON.stringify({ run: run.name, acceptedBy, acceptedAt: new Date().toISOString() }, null, 2)}\n`);
    return run.name;
  }
}

/** One run of a sub-epic: walked by hand or run by its browser story tests. */
export class Run {
  constructor(readonly dir: string) {}

  get name(): string {
    return path.basename(this.dir);
  }

  /** Whether the run has its results: a folder without them is no run. */
  get isThere(): boolean {
    return existsSync(path.join(this.dir, RESULTS_FILE));
  }

  get subEpic(): SubEpicRuns {
    return new SubEpicRuns(path.dirname(this.dir));
  }

  /** Each step's row, as recorded. */
  get steps(): StepRow[] {
    const file = path.join(this.dir, RESULTS_FILE);
    return existsSync(file) ? (JSON.parse(readFileSync(file, 'utf8')) as StepRow[]) : [];
  }

  /** The run's regression review, when it has one. */
  get review(): Review | undefined {
    const file = path.join(this.dir, REVIEW_FILE);
    return existsSync(file) ? (JSON.parse(readFileSync(file, 'utf8')) as Review) : undefined;
  }

  /**
   * The run its own report compares its screens with: its sub-epic's accepted run when that is another run, else the
   * run before it by name, else none.
   */
  get previous(): Run | undefined {
    const accepted = this.subEpic.baseline;
    if (accepted && accepted.name !== this.name) return accepted;
    const runs = this.subEpic.runs;
    const at = runs.findIndex(run => run.name === this.name);
    return at > 0 ? runs[at - 1] : undefined;
  }

  /**
   * Each step of this run paired with the same step of `other` (an accepted walk, or the last accepted run), saying
   * whether its screen changed, by pixels: the share of 8px blocks whose average grey moved by more than 6 levels.
   */
  pairsAgainst(other: Run): StepPair[] {
    const ours = new Map(this.steps.map(row => [row.key, row]));
    const theirs = new Map(other.steps.map(row => [row.key, row]));
    const keys = [...new Set([...ours.keys(), ...theirs.keys()])];
    return keys.map(key => {
      const mine = ours.get(key);
      const their = theirs.get(key);
      if (!their) return { key, change: 'new', changedPercent: 100, ours: mine };
      if (!mine) return { key, change: 'gone', changedPercent: 100, theirs: their };
      const look = lookDifference(path.join(other.dir, their.screenshot), path.join(this.dir, mine.screenshot));
      return { key, change: look.changedBlocks >= LOOK_GATE_BLOCKS ? 'changed' : 'same', changedPercent: look.changedPercent, changedArea: look.area, ours: mine, theirs: their };
    });
  }

  /** The pairs against `other`, by default the sub-epic's baseline, whose screen is not the same: what to judge. */
  changedAgainst(other: Run | undefined = this.subEpic.baseline): StepPair[] {
    if (!other) throw new ReviewRefused(`${path.basename(this.subEpic.dir)} has no accepted run to compare ${this.name} with`);
    return this.pairsAgainst(other).filter(pair => pair.change !== 'same');
  }

  /**
   * The run's rows with their three checks: the test's result, the judge's verdict (does the screen show what the step
   * says), and whether the screen is the same as the previous run's. A step the judge has not seen whose screen is the
   * same as the previous run's takes that run's verdict: a judge pass is needed only for new or changed screens.
   */
  get checkedSteps(): StepRow[] {
    const rows = this.steps;
    const previous = this.previous;
    if (!previous) return rows;
    const earlierRows = new Map(previous.checkedSteps.map(row => [row.key, row]));
    const pairs = new Map(this.pairsAgainst(previous).map(pair => [pair.key, pair]));
    const review = this.review;
    const reviewed = review?.against === previous.name ? review.pairs : {};
    return rows.map(row => {
      const pair = pairs.get(row.key);
      const checked: StepRow = { ...row, change: pair?.change ?? 'new', previous: previous.name };
      if (pair?.change === 'changed') {
        const judged = reviewed[row.key];
        Object.assign(checked, { previousShot: pair.theirs?.screenshot, changedPercent: pair.changedPercent, changedArea: pair.changedArea, changeReview: judged ? `${judged.verdict}: ${judged.reason}` : undefined });
      }
      const earlier = earlierRows.get(row.key);
      if (!row.verdict && pair?.change === 'same' && earlier?.verdict) return { ...checked, verdict: earlier.verdict, reason: earlier.reason, judgedIn: earlier.judgedIn ?? previous.name };
      return checked;
    });
  }

  /**
   * The judge's verdict on one step a test ran: does its screen show what its Given, When or Then says. Kept on the
   * step's row; judging it again replaces it.
   */
  judge(key: string, verdict: Verdict, reason: string): StepRow {
    if (!JUDGE_VERDICTS.includes(verdict)) throw new ReviewRefused(`no judge verdict ${verdict}: give ${JUDGE_VERDICTS.join(' or ')}`);
    if (reason.trim() === '') throw new ReviewRefused(`a judge verdict on ${key} needs its reason`);
    const rows = this.steps;
    const row = rows.find(each => each.key === key);
    if (!row) throw new ReviewRefused(`no step ${key} in ${this.name}`);
    row.verdict = verdict;
    row.reason = reason;
    this.keep(rows);
    return row;
  }

  /** A step of a walk by hand, its screenshot saved in the run folder, with its verdict. Walking it again replaces it. */
  addWalkedStep(step: StepRow): StepRow {
    if (!existsSync(path.join(this.dir, step.screenshot))) throw new ReviewRefused(`save the step's screenshot at ${path.join(this.dir, step.screenshot)} first`);
    if (!JUDGE_VERDICTS.includes(step.verdict as Verdict)) throw new ReviewRefused(`no walk verdict ${step.verdict}: give ${JUDGE_VERDICTS.join(' or ')}`);
    const walked: StepRow = { ...step, by: 'walked by hand' };
    this.keep([...this.steps.filter(earlier => earlier.key !== step.key), walked]);
    return walked;
  }

  /** Record the verdict on one changed pair of this run against `against`. */
  recordVerdict(against: Run, key: string, review: PairReview): Review {
    if (!this.changedAgainst(against).some(pair => pair.key === key)) throw new ReviewRefused(`no changed step ${key} in ${this.name}`);
    if (review.reason.trim() === '') throw new ReviewRefused(`a verdict on ${key} needs its reason`);
    if (review.verdict === 'intended' && !review.cites?.trim()) throw new ReviewRefused(`an intended change to ${key} cites the story or code change behind it`);
    if (review.verdict === 'regression caught' && !review.cites?.trim()) throw new ReviewRefused(`a regression caught on ${key} names the test that fails for it`);
    const earlier = this.review;
    const kept: Review = { against: against.name, pairs: earlier?.against === against.name ? { ...earlier.pairs } : {} };
    kept.pairs[key] = review;
    writeFileSync(path.join(this.dir, REVIEW_FILE), `${JSON.stringify(kept, null, 2)}\n`);
    return kept;
  }

  /** Each changed pair with no verdict yet, or with a verdict other than intended: what keeps the run from being accepted. */
  openPairs(against: Run): string[] {
    const review = this.review;
    const pairs = review?.against === against.name ? review.pairs : {};
    return this.changedAgainst(against).filter(pair => pairs[pair.key]?.verdict !== 'intended').map(pair => pair.key);
  }

  /** A run is reviewed once every changed pair has a verdict. */
  isReviewed(against: Run): boolean {
    const pairs = this.review?.pairs ?? {};
    return this.changedAgainst(against).every(pair => pairs[pair.key] !== undefined);
  }

  /**
   * What Python reads of the run, against `against` when it is compared with one: its steps, the steps whose screen
   * changed, those with no verdict yet, and those missed: judged missed by the tests, or walked or judged as missing
   * the intent.
   */
  summary(against?: Run): RunSummary {
    const changed = against ? this.changedAgainst(against).map(pair => pair.key) : [];
    const verdicts = this.review?.pairs ?? {};
    const missedByTests = Object.entries(verdicts).filter(([, review]) => review.verdict === 'missed by the tests').map(([key]) => key);
    const steps = this.steps;
    return {
      steps: steps.length,
      changed_steps: changed,
      unjudged_steps: changed.filter(key => verdicts[key] === undefined),
      missed_steps: [...missedByTests, ...steps.filter(row => row.verdict === 'misses the intent').map(row => row.key)],
    };
  }

  /** Write the run's summary beside it, against `against` when it is compared with one. */
  keepSummary(against?: Run): RunSummary {
    const summary = this.summary(against);
    writeFileSync(path.join(this.dir, SUMMARY_FILE), `${JSON.stringify(summary, null, 2)}\n`);
    return summary;
  }

  private keep(rows: StepRow[]): void {
    writeFileSync(path.join(this.dir, RESULTS_FILE), `${JSON.stringify(rows, null, 2)}\n`);
  }
}

/** How many 8px blocks' average grey moved, and their share in percent; screens of different sizes count as all changed. */
function lookDifference(theirFile: string, ourFile: string): { changedBlocks: number; changedPercent: number; area?: Area } {
  const everything = { changedBlocks: Number.POSITIVE_INFINITY, changedPercent: 100, area: { left: 0, top: 0, width: 1, height: 1 } };
  if (!existsSync(theirFile) || !existsSync(ourFile)) return everything;
  const one = PNG.sync.read(readFileSync(theirFile));
  const two = PNG.sync.read(readFileSync(ourFile));
  if (one.width !== two.width || one.height !== two.height) return everything;
  let changed = 0;
  let blocks = 0;
  const box = { left: Number.POSITIVE_INFINITY, top: Number.POSITIVE_INFINITY, right: 0, bottom: 0 };
  for (let by = 0; by + LOOK_BLOCK_PX <= one.height; by += LOOK_BLOCK_PX) {
    for (let bx = 0; bx + LOOK_BLOCK_PX <= one.width; bx += LOOK_BLOCK_PX) {
      blocks++;
      if (Math.abs(blockGrey(one, bx, by) - blockGrey(two, bx, by)) <= LOOK_BLOCK_LIMIT) continue;
      changed++;
      box.left = Math.min(box.left, bx);
      box.top = Math.min(box.top, by);
      box.right = Math.max(box.right, bx + LOOK_BLOCK_PX);
      box.bottom = Math.max(box.bottom, by + LOOK_BLOCK_PX);
    }
  }
  const area = changed ? { left: box.left / one.width, top: box.top / one.height, width: (box.right - box.left) / one.width, height: (box.bottom - box.top) / one.height } : undefined;
  return { changedBlocks: changed, changedPercent: blocks ? (100 * changed) / blocks : 0, area };
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
