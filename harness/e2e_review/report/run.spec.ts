import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { PNG } from 'pngjs';
import { beforeEach, describe, expect, it } from 'vitest';
import { RESULTS_FILE, ReviewRefused, Run, type StepRow, SubEpicRuns } from './run';

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
    expect(new SubEpicRuns(subEpicDir).baseline).toBeUndefined();
  });

  it('should refuse to list changed pairs with nothing to compare with', () => {
    expect(() => new Run(run(subEpicDir, 'run-1', 255)).changedAgainst()).toThrow(ReviewRefused);
  });

  it('should take its first run as the baseline once the person accepts it', () => {
    new SubEpicRuns(subEpicDir).accept(new Run(run(subEpicDir, 'run-1', 255)), 'Jeff');
    expect(new SubEpicRuns(subEpicDir).baseline!.name).toBe('run-1');
  });
});

describe('a run compared with the accepted run', () => {
  let subEpicDir: string;
  let ours: Run;
  const baseline = () => new SubEpicRuns(subEpicDir).baseline!;
  const accept = () => new SubEpicRuns(subEpicDir).accept(ours, 'Jeff');
  beforeEach(() => {
    subEpicDir = newSubEpic();
    new SubEpicRuns(subEpicDir).accept(new Run(run(subEpicDir, 'run-1', 255)), 'Jeff');
    ours = new Run(run(subEpicDir, 'run-2', 0));
  });

  it('should choose the accepted run to compare with', () => {
    expect(baseline().name).toBe('run-1');
  });

  it('should list only the step whose screen changed', () => {
    expect(ours.changedAgainst().map(pair => pair.key)).toEqual([THEN.key]);
  });

  it('should not count as reviewed with a changed pair unjudged', () => {
    expect(ours.isReviewed(baseline())).toBe(false);
  });

  describe('with its changed pair judged intended', () => {
    beforeEach(() => {
      ours.recordVerdict(baseline(), THEN.key, { verdict: 'intended', reason: 'Tags are drawn dark now.', cites: 'commit abc123' });
    });

    it('should count as reviewed', () => {
      expect(ours.isReviewed(baseline())).toBe(true);
    });

    it('should leave nothing open', () => {
      expect(ours.openPairs(baseline())).toEqual([]);
    });

    it('should become the baseline once the person accepts it', () => {
      accept();
      expect(baseline().name).toBe('run-2');
    });
  });

  describe('with its changed pair judged missed by the tests', () => {
    beforeEach(() => {
      ours.recordVerdict(baseline(), THEN.key, { verdict: 'missed by the tests', reason: 'The tag is black on black.' });
    });

    it('should count as reviewed', () => {
      expect(ours.isReviewed(baseline())).toBe(true);
    });

    it("should refuse the person's acceptance, naming the step", () => {
      expect(accept).toThrow(THEN.key);
    });

    it('should leave the baseline where it was', () => {
      expect(accept).toThrow(ReviewRefused);
      expect(baseline().name).toBe('run-1');
    });
  });

  describe('with its changed pair judged noise', () => {
    it("should refuse the person's acceptance", () => {
      ours.recordVerdict(baseline(), THEN.key, { verdict: 'noise', reason: 'A clock moved.' });
      expect(accept).toThrow(ReviewRefused);
    });
  });

  it('should refuse an intended verdict that cites no change', () => {
    expect(() => ours.recordVerdict(baseline(), THEN.key, { verdict: 'intended', reason: 'Looks fine.' })).toThrow(ReviewRefused);
  });

  it('should refuse a regression caught verdict that names no failing test', () => {
    expect(() => ours.recordVerdict(baseline(), THEN.key, { verdict: 'regression caught', reason: 'Broken.' })).toThrow(ReviewRefused);
  });

  it('should refuse a verdict on a step whose screen did not change', () => {
    expect(() => ours.recordVerdict(baseline(), GIVEN.key, { verdict: 'noise', reason: 'n/a' })).toThrow(ReviewRefused);
  });

  it('should keep its verdicts in the run folder', () => {
    ours.recordVerdict(baseline(), THEN.key, { verdict: 'noise', reason: 'A clock moved.' });
    expect(JSON.parse(readFileSync(path.join(ours.dir, 'review.json'), 'utf8')).pairs[THEN.key].verdict).toBe('noise');
  });

  it('should keep the accepted run named in the sub-epic folder', () => {
    expect(existsSync(path.join(subEpicDir, 'baseline.json'))).toBe(true);
  });
});

describe("a judge pass on a run's screens", () => {
  let judged: Run;
  const rows = () => judged.steps;
  beforeEach(() => {
    judged = new Run(run(newSubEpic(), 'run-1', 255));
  });

  it("should keep the judge's verdict and reason on the step's row", () => {
    judged.judge(THEN.key, 'misses the intent', 'The card shows no tag.');
    expect(rows()[1]).toMatchObject({ verdict: 'misses the intent', reason: 'The card shows no tag.', result: 'pass' });
  });

  it('should replace the verdict when the step is judged again', () => {
    judged.judge(THEN.key, 'misses the intent', 'No tag.');
    judged.judge(THEN.key, 'meets the intent', 'The card shows billing.');
    expect(rows()[1].verdict).toBe('meets the intent');
  });

  it('should refuse a step the run does not have', () => {
    expect(() => judged.judge('No › such › 1 step', 'meets the intent', 'Fine.')).toThrow(ReviewRefused);
  });

  it('should refuse a verdict with no reason', () => {
    expect(() => judged.judge(THEN.key, 'meets the intent', ' ')).toThrow(ReviewRefused);
  });
});

describe('a walk by hand', () => {
  let walk: Run;
  beforeEach(() => {
    const dir = path.join(newSubEpic(), 'walk-1');
    mkdirSync(path.join(dir, 'screens'), { recursive: true });
    writeFileSync(path.join(dir, RESULTS_FILE), '[]');
    writeFileSync(path.join(dir, GIVEN.screenshot), screenshot(255));
    walk = new Run(dir);
  });

  it('should keep a walked step with its verdict, as walked by hand', () => {
    walk.addWalkedStep({ ...GIVEN, verdict: 'misses the intent', reason: 'The board is empty.' });
    expect(walk.steps).toEqual([{ ...GIVEN, by: 'walked by hand', verdict: 'misses the intent', reason: 'The board is empty.' }]);
  });

  it('should replace a step walked again', () => {
    walk.addWalkedStep({ ...GIVEN, verdict: 'misses the intent', reason: 'Empty.' });
    walk.addWalkedStep({ ...GIVEN, verdict: 'meets the intent', reason: 'Shows the ticket.' });
    expect(walk.steps.map(step => step.verdict)).toEqual(['meets the intent']);
  });

  it('should refuse a step whose screenshot was not saved', () => {
    expect(() => walk.addWalkedStep({ ...THEN, verdict: 'meets the intent', reason: 'Fine.' })).toThrow(ReviewRefused);
  });

  it('should count a step that misses the intent as missed in its summary', () => {
    walk.addWalkedStep({ ...GIVEN, verdict: 'misses the intent', reason: 'Empty.' });
    walk.keepSummary();
    expect(JSON.parse(readFileSync(path.join(walk.dir, 'changed.json'), 'utf8'))).toEqual({ steps: 1, changed_steps: [], unjudged_steps: [], missed_steps: [GIVEN.key] });
  });
});

describe("a compared run's summary", () => {
  it('should name the changed step, unjudged, until a verdict is recorded on it', () => {
    const subEpicDir = newSubEpic();
    new SubEpicRuns(subEpicDir).accept(new Run(run(subEpicDir, 'run-1', 255)), 'Jeff');
    const ours = new Run(run(subEpicDir, 'run-2', 0));
    const against = new SubEpicRuns(subEpicDir).baseline!;
    expect(ours.summary(against)).toEqual({ steps: 2, changed_steps: [THEN.key], unjudged_steps: [THEN.key], missed_steps: [] });
    ours.recordVerdict(against, THEN.key, { verdict: 'missed by the tests', reason: 'Black on black.' });
    expect(ours.summary(against)).toEqual({ steps: 2, changed_steps: [THEN.key], unjudged_steps: [], missed_steps: [THEN.key] });
  });
});
