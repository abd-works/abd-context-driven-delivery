import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { PNG } from 'pngjs';
import { beforeEach, describe, expect, it } from 'vitest';
import { RESULTS_FILE, type StepRow } from './report';
import { acceptRun, baselineOf, changedPairs, isReviewed, openPairs, recordVerdict, ReviewRefused } from './review';

const GIVEN: StepRow = { key: 'Tag Ticket Session › Tag a ticket › 1 Given the ticket has no tags', step: 'Given the ticket has no tags', screenshot: 'screens/1.png', by: 'run by a test', result: 'pass' };
const THEN: StepRow = { key: 'Tag Ticket Session › Tag a ticket › 2 Then the card shows the tag billing', step: 'Then the card shows the tag billing', screenshot: 'screens/2.png', by: 'run by a test', result: 'pass' };

function screenshot(grey: number): Buffer {
  const image = new PNG({ width: 16, height: 16 });
  image.data.fill(grey);
  return PNG.sync.write(image);
}

/** A run whose Given is white and whose Then is `thenGrey`. */
function run(subEpicDir: string, name: string, thenGrey: number): string {
  const runDir = path.join(subEpicDir, name);
  mkdirSync(path.join(runDir, 'screens'), { recursive: true });
  writeFileSync(path.join(runDir, RESULTS_FILE), JSON.stringify([GIVEN, THEN]));
  writeFileSync(path.join(runDir, GIVEN.screenshot), screenshot(255));
  writeFileSync(path.join(runDir, THEN.screenshot), screenshot(thenGrey));
  return runDir;
}

const newSubEpic = () => path.join(mkdtempSync(path.join(tmpdir(), 'review-')), 'maintain-tickets');

describe('a sub-epic with no accepted run', () => {
  let subEpicDir: string;
  beforeEach(() => {
    subEpicDir = newSubEpic();
  });

  it('should have no baseline', () => {
    run(subEpicDir, 'run-1', 255);
    expect(baselineOf(subEpicDir)).toBeUndefined();
  });

  it('should refuse to list changed pairs with nothing to compare with', () => {
    expect(() => changedPairs(run(subEpicDir, 'run-1', 255))).toThrow(ReviewRefused);
  });

  it('should take its first run as the baseline once the person accepts it', () => {
    acceptRun(run(subEpicDir, 'run-1', 255), 'Jeff');
    expect(path.basename(baselineOf(subEpicDir)!)).toBe('run-1');
  });
});

describe('a run compared with the accepted run', () => {
  let subEpicDir: string;
  let runDir: string;
  const baseline = () => baselineOf(subEpicDir)!;
  beforeEach(() => {
    subEpicDir = newSubEpic();
    acceptRun(run(subEpicDir, 'run-1', 255), 'Jeff');
    runDir = run(subEpicDir, 'run-2', 0);
  });

  it('should choose the accepted run to compare with', () => {
    expect(path.basename(baseline())).toBe('run-1');
  });

  it('should list only the step whose screen changed', () => {
    expect(changedPairs(runDir).map(pair => pair.key)).toEqual([THEN.key]);
  });

  it('should not count as reviewed with a changed pair unjudged', () => {
    expect(isReviewed(runDir, baseline())).toBe(false);
  });

  describe('with its changed pair judged intended', () => {
    beforeEach(() => {
      recordVerdict(runDir, baseline(), THEN.key, { verdict: 'intended', reason: 'Tags are drawn dark now.', cites: 'commit abc123' });
    });

    it('should count as reviewed', () => {
      expect(isReviewed(runDir, baseline())).toBe(true);
    });

    it('should leave nothing open', () => {
      expect(openPairs(runDir, baseline())).toEqual([]);
    });

    it('should become the baseline once the person accepts it', () => {
      acceptRun(runDir, 'Jeff');
      expect(path.basename(baseline())).toBe('run-2');
    });
  });

  describe('with its changed pair judged missed by the tests', () => {
    beforeEach(() => {
      recordVerdict(runDir, baseline(), THEN.key, { verdict: 'missed by the tests', reason: 'The tag is black on black.' });
    });

    it('should count as reviewed', () => {
      expect(isReviewed(runDir, baseline())).toBe(true);
    });

    it("should refuse the person's acceptance, naming the step", () => {
      expect(() => acceptRun(runDir, 'Jeff')).toThrow(THEN.key);
    });

    it('should leave the baseline where it was', () => {
      expect(() => acceptRun(runDir, 'Jeff')).toThrow(ReviewRefused);
      expect(path.basename(baseline())).toBe('run-1');
    });
  });

  describe('with its changed pair judged noise', () => {
    it("should refuse the person's acceptance", () => {
      recordVerdict(runDir, baseline(), THEN.key, { verdict: 'noise', reason: 'A clock moved.' });
      expect(() => acceptRun(runDir, 'Jeff')).toThrow(ReviewRefused);
    });
  });

  it('should refuse an intended verdict that cites no change', () => {
    expect(() => recordVerdict(runDir, baseline(), THEN.key, { verdict: 'intended', reason: 'Looks fine.' })).toThrow(ReviewRefused);
  });

  it('should refuse a regression caught verdict that names no failing test', () => {
    expect(() => recordVerdict(runDir, baseline(), THEN.key, { verdict: 'regression caught', reason: 'Broken.' })).toThrow(ReviewRefused);
  });

  it('should refuse a verdict on a step whose screen did not change', () => {
    expect(() => recordVerdict(runDir, baseline(), GIVEN.key, { verdict: 'noise', reason: 'n/a' })).toThrow(ReviewRefused);
  });

  it('should keep its verdicts in the run folder', () => {
    recordVerdict(runDir, baseline(), THEN.key, { verdict: 'noise', reason: 'A clock moved.' });
    expect(JSON.parse(readFileSync(path.join(runDir, 'review.json'), 'utf8')).pairs[THEN.key].verdict).toBe('noise');
  });

  it('should keep the accepted run named in the sub-epic folder', () => {
    expect(existsSync(path.join(subEpicDir, 'baseline.json'))).toBe(true);
  });
});
