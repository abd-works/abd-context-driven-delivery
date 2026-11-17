/**
 * The regression review of an end-to-end run: which accepted run it is compared with, a verdict on each pair whose
 * screen changed, and the person's acceptance that makes a reviewed run the next baseline.
 *
 * A sub-epic's folder (`<epic>/<sub-epic>/`) holds its runs and `baseline.json`, naming the accepted run. A run's
 * folder holds `review.json`: its verdict on each changed pair, keyed by step.
 */

import { existsSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

import { RESULTS_FILE, type StepPair, type StepRow, stepPairs, type Verdict } from './report';

export const BASELINE_FILE = 'baseline.json';
export const REVIEW_FILE = 'review.json';

export type ReviewVerdict = 'intended' | 'regression caught' | 'missed by the tests' | 'noise';

/** One changed pair's verdict. `cites` is the story or code change an intended pair follows from, or the failing test. */
export type PairReview = { verdict: ReviewVerdict; reason: string; cites?: string };

export type Review = { against: string; pairs: Record<string, PairReview> };

export class ReviewRefused extends Error {}

/** The run the sub-epic's next run is compared with: the last one the person accepted, or none yet. */
export function baselineOf(subEpicDir: string): string | undefined {
  const file = path.join(subEpicDir, BASELINE_FILE);
  if (!existsSync(file)) return undefined;
  const run = (JSON.parse(readFileSync(file, 'utf8')) as { run: string }).run;
  return existsSync(path.join(subEpicDir, run, RESULTS_FILE)) ? path.join(subEpicDir, run) : undefined;
}

/** The sub-epic's runs, oldest name first. */
export function runsOf(subEpicDir: string): string[] {
  if (!existsSync(subEpicDir)) return [];
  return readdirSync(subEpicDir)
    .filter(entry => statSync(path.join(subEpicDir, entry)).isDirectory() && existsSync(path.join(subEpicDir, entry, RESULTS_FILE)))
    .sort()
    .map(entry => path.join(subEpicDir, entry));
}

/** The pairs of `runDir` against its baseline (or `againstDir`) whose screen is not the same: what the agent must judge. */
export function changedPairs(runDir: string, againstDir = baselineOf(path.dirname(runDir))): StepPair[] {
  if (!againstDir) throw new ReviewRefused(`${path.basename(path.dirname(runDir))} has no accepted run to compare ${path.basename(runDir)} with`);
  return stepPairs(runDir, againstDir).filter(pair => pair.change !== 'same');
}

export function reviewOf(runDir: string): Review | undefined {
  const file = path.join(runDir, REVIEW_FILE);
  return existsSync(file) ? (JSON.parse(readFileSync(file, 'utf8')) as Review) : undefined;
}

/** Record the verdict on one changed pair of `runDir` against `againstDir`. */
export function recordVerdict(runDir: string, againstDir: string, key: string, review: PairReview): Review {
  if (!changedPairs(runDir, againstDir).some(pair => pair.key === key)) throw new ReviewRefused(`no changed step ${key} in ${path.basename(runDir)}`);
  if (review.reason.trim() === '') throw new ReviewRefused(`a verdict on ${key} needs its reason`);
  if (review.verdict === 'intended' && !review.cites?.trim()) throw new ReviewRefused(`an intended change to ${key} cites the story or code change behind it`);
  if (review.verdict === 'regression caught' && !review.cites?.trim()) throw new ReviewRefused(`a regression caught on ${key} names the test that fails for it`);
  const earlier = reviewOf(runDir);
  const kept: Review = { against: path.basename(againstDir), pairs: earlier?.against === path.basename(againstDir) ? { ...earlier.pairs } : {} };
  kept.pairs[key] = review;
  writeFileSync(path.join(runDir, REVIEW_FILE), `${JSON.stringify(kept, null, 2)}\n`);
  return kept;
}

const JUDGE_VERDICTS: Verdict[] = ['meets the intent', 'misses the intent'];

/**
 * The judge's verdict on one step a test ran: does its screen show what its Given, When or Then says. Kept on the step's
 * row in `results.json`; judging it again replaces it.
 */
export function judgeStep(runDir: string, key: string, verdict: Verdict, reason: string): StepRow {
  if (!JUDGE_VERDICTS.includes(verdict)) throw new ReviewRefused(`no judge verdict ${verdict}: give ${JUDGE_VERDICTS.join(' or ')}`);
  if (reason.trim() === '') throw new ReviewRefused(`a judge verdict on ${key} needs its reason`);
  const file = path.join(runDir, RESULTS_FILE);
  const rows = JSON.parse(readFileSync(file, 'utf8')) as StepRow[];
  const row = rows.find(each => each.key === key);
  if (!row) throw new ReviewRefused(`no step ${key} in ${path.basename(runDir)}`);
  row.verdict = verdict;
  row.reason = reason;
  writeFileSync(file, `${JSON.stringify(rows, null, 2)}
`);
  return row;
}

/** Each changed pair with no verdict yet, or with a verdict other than intended: what keeps the run from being accepted. */
export function openPairs(runDir: string, againstDir: string): string[] {
  const review = reviewOf(runDir);
  const pairs = review?.against === path.basename(againstDir) ? review.pairs : {};
  return changedPairs(runDir, againstDir).filter(pair => pairs[pair.key]?.verdict !== 'intended').map(pair => pair.key);
}

/** A run is reviewed once every changed pair has a verdict. */
export function isReviewed(runDir: string, againstDir: string): boolean {
  const pairs = reviewOf(runDir)?.pairs ?? {};
  return changedPairs(runDir, againstDir).every(pair => pairs[pair.key] !== undefined);
}

/**
 * The person accepts `runDir`: it becomes its sub-epic's baseline. Refused while a changed pair is unjudged or judged
 * anything but intended, because only an explained change may move the baseline. The first run, with nothing to
 * compare with, is accepted as it is.
 */
export function acceptRun(runDir: string, acceptedBy: string): string {
  const subEpicDir = path.dirname(runDir);
  const against = baselineOf(subEpicDir);
  if (against && path.resolve(against) !== path.resolve(runDir)) {
    const open = openPairs(runDir, against);
    if (open.length) throw new ReviewRefused(`${path.basename(runDir)} has ${open.length} changed step(s) not judged intended: ${open.join('; ')}`);
  }
  writeFileSync(path.join(subEpicDir, BASELINE_FILE), `${JSON.stringify({ run: path.basename(runDir), acceptedBy, acceptedAt: new Date().toISOString() }, null, 2)}\n`);
  return path.basename(runDir);
}

/**
 * `npx tsx review.ts pairs <run> [--against <run>]`: the changed pairs as JSON.
 * `npx tsx review.ts verdict <run> <step key> <verdict> <reason> [--cites <change>] [--against <run>]`: record one verdict.
 * `npx tsx review.ts accept <run> --by <person>`: make the run its sub-epic's baseline.
 * `npx tsx review.ts judge <run> <step key> <meets the intent|misses the intent> <reason>`: the judge's verdict on a step.
 */
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  const option = (name: string) => {
    const at = args.indexOf(name);
    return at >= 0 ? args.splice(at, 2)[1] : undefined;
  };
  const against = option('--against');
  const cites = option('--cites');
  const by = option('--by');
  const [command, run, ...rest] = args;
  const runDir = path.resolve(run ?? '');
  const againstDir = against ? path.resolve(against) : baselineOf(path.dirname(runDir));
  try {
    if (command === 'pairs') {
      const pairs = changedPairs(runDir, againstDir).map(pair => ({ key: pair.key, change: pair.change, changedPercent: Number(pair.changedPercent.toFixed(2)), ours: pair.ours?.screenshot, theirs: pair.theirs?.screenshot }));
      console.log(JSON.stringify(pairs, null, 2));
    } else if (command === 'verdict') {
      const [key = '', verdict = '', reason = ''] = rest;
      if (!againstDir) throw new ReviewRefused('no run to compare with');
      recordVerdict(runDir, againstDir, key, { verdict: verdict as ReviewVerdict, reason, cites });
      console.log(`Recorded ${verdict} on ${key}`);
    } else if (command === 'judge') {
      const [key = '', verdict = '', reason = ''] = rest;
      judgeStep(runDir, key, verdict as Verdict, reason);
      console.log(`Judged ${verdict} on ${key}`);
    } else if (command === 'accept') {
      console.log(`Baseline: ${acceptRun(runDir, by ?? 'unknown')}`);
    } else {
      console.error('Usage: review.ts pairs|verdict|judge|accept <run folder> ...');
      process.exit(1);
    }
  } catch (refused) {
    console.error(refused instanceof Error ? refused.message : String(refused));
    process.exit(1);
  }
}
