/**
 * The command line of an end-to-end run's review: list the changed pairs, record a verdict on one, record a judge's
 * verdict or a walked step, accept a run as its sub-epic's baseline, and write a run's summary. Each command reads and
 * changes the run through *Run* (`run.ts`) and then keeps the run's summary beside it, which Python reads.
 *
 * `npx tsx review.ts pairs <run> [--against <run>]`: the changed pairs as JSON.
 * `npx tsx review.ts verdict <run> <step key> <verdict> <reason> [--cites <change>] [--against <run>]`: record one verdict.
 * `npx tsx review.ts judge <run> <step key> <meets the intent|misses the intent> <reason>`: the judge's verdict on a step.
 * `npx tsx review.ts walk-step <run> <step key> <step text> <screenshot> <meets the intent|misses the intent> <reason>`: a walked step.
 * `npx tsx review.ts accept <run> --by <person>`: make the run its sub-epic's baseline.
 * `npx tsx review.ts summary <run> [--against <run>]`: write and print the run's summary.
 */

import path from 'node:path';
import { pathToFileURL } from 'node:url';

import { type ReviewVerdict, ReviewRefused, Run, type Verdict } from './run';

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  const option = (name: string) => {
    const at = args.indexOf(name);
    return at >= 0 ? args.splice(at, 2)[1] : undefined;
  };
  const againstFolder = option('--against');
  const cites = option('--cites');
  const by = option('--by');
  const [command, folder, ...rest] = args;
  const run = new Run(path.resolve(folder ?? ''));
  const against = againstFolder ? new Run(path.resolve(againstFolder)) : run.subEpic.baseline;
  try {
    if (command === 'pairs') {
      const pairs = run.changedAgainst(against).map(pair => ({ key: pair.key, change: pair.change, changedPercent: Number(pair.changedPercent.toFixed(2)), ours: pair.ours?.screenshot, theirs: pair.theirs?.screenshot }));
      run.keepSummary(against);
      console.log(JSON.stringify(pairs, null, 2));
    } else if (command === 'verdict') {
      const [key = '', verdict = '', reason = ''] = rest;
      if (!against) throw new ReviewRefused('no run to compare with');
      run.recordVerdict(against, key, { verdict: verdict as ReviewVerdict, reason, cites });
      run.keepSummary(against);
      console.log(`Recorded ${verdict} on ${key}`);
    } else if (command === 'judge') {
      const [key = '', verdict = '', reason = ''] = rest;
      run.judge(key, verdict as Verdict, reason);
      run.keepSummary(against);
      console.log(`Judged ${verdict} on ${key}`);
    } else if (command === 'walk-step') {
      const [key = '', step = '', screenshot = '', verdict = '', reason = ''] = rest;
      run.addWalkedStep({ key, step, screenshot, by: 'walked by hand', verdict: verdict as Verdict, reason });
      run.keepSummary();
      console.log(`Walked ${key}: ${verdict}`);
    } else if (command === 'accept') {
      console.log(`Baseline: ${run.subEpic.accept(run, by ?? 'unknown')}`);
    } else if (command === 'summary') {
      console.log(JSON.stringify(run.keepSummary(against), null, 2));
    } else {
      console.error('Usage: review.ts pairs|verdict|judge|walk-step|accept|summary <run folder> ...');
      process.exit(1);
    }
  } catch (refused) {
    console.error(refused instanceof Error ? refused.message : String(refused));
    process.exit(1);
  }
}
