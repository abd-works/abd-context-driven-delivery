import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { PNG } from 'pngjs';
import { beforeEach, describe, expect, it } from 'vitest';
import { placeOf, writeCompareReport, writeHistoryReport, writeStoryMapReport, writeWalkReport } from './report';
import { RESULTS_FILE, Run, type StepRow } from './run';

const STORY = 'Maintain Tickets';
const SCENARIO = 'Rename a ticket';
const GIVEN_SHOT = 'screens/maintain-tickets-rename-a-ticket-1-given.png';
const THEN_SHOT = 'screens/maintain-tickets-rename-a-ticket-2-then.png';

function screenshot(grey: number): Buffer {
  const image = new PNG({ width: 16, height: 16 });
  image.data.fill(grey);
  return PNG.sync.write(image);
}

const MEETS: StepRow = {
  key: `${STORY} › ${SCENARIO} › 1 Given a ticket called alpha on the board`,
  step: 'Given a ticket called alpha on the board',
  screenshot: GIVEN_SHOT,
  by: 'walked by hand',
  verdict: 'meets the intent',
  reason: 'The board shows a card titled alpha in Discovery.',
};

const MISSES: StepRow = {
  key: `${STORY} › ${SCENARIO} › 2 Then the card reads beta`,
  step: 'Then the card reads beta',
  screenshot: THEN_SHOT,
  by: 'walked by hand',
  verdict: 'misses the intent',
  reason: 'The card still reads alpha <until reload>.',
};

/** A run folder `<root>/<epic>/<sub-epic>/<run>` holding the given rows and both screenshots. */
function runFolder(rows: StepRow[], run = 'walk-1', root = mkdtempSync(path.join(tmpdir(), 'walk-report-'))): { root: string; runDir: string } {
  const runDir = path.join(root, 'move-work-forward-on-session-board', 'maintain-tickets', run);
  mkdirSync(path.join(runDir, 'screens'), { recursive: true });
  writeFileSync(path.join(runDir, RESULTS_FILE), JSON.stringify(rows));
  writeFileSync(path.join(runDir, GIVEN_SHOT), screenshot(255));
  writeFileSync(path.join(runDir, THEN_SHOT), screenshot(0));
  return { root, runDir };
}

describe('a walk report', () => {
  describe('that has been written for a walk with a step that meets the intent and one that misses it', () => {
    let page: string;
    beforeEach(() => {
      page = readFileSync(writeWalkReport(new Run(runFolder([MISSES, MEETS]).runDir)), 'utf8');
    });

    it('should name the sub-epic from the run folder', () => {
      expect(page).toContain('Move Work Forward On Session Board › Maintain Tickets');
    });

    it("should show each step's Given, When or Then text", () => {
      expect(page).toContain('1 Given a ticket called alpha on the board');
    });

    it('should list the steps in their numbered order', () => {
      expect(page.indexOf('1 Given a ticket')).toBeLessThan(page.indexOf('2 Then the card reads beta'));
    });

    it("should show each step's judge verdict among its checks", () => {
      expect(page).toContain('<div class="check fail"><span class="check-name">Judge</span><span class="check-value">misses the intent</span></div>');
    });

    it("should show each step's reason, escaped", () => {
      expect(page).toContain('The card still reads alpha &lt;until reload&gt;.');
    });

    it('should embed one screenshot for each step inside the page', () => {
      expect(page.match(/<img data-shot=/g)).toHaveLength(2);
    });

    it('should link each screenshot to its full-size file in the run folder', () => {
      expect(page).toContain('href="screens/maintain-tickets-rename-a-ticket-2-then.png"');
    });

    it('should open the scenario that has a step that misses the intent', () => {
      expect(page).toMatch(/<details class="scenario failing" id="[^"]+" open>/);
    });

    it('should count the steps that meet and miss for the story', () => {
      expect(page).toMatch(/Maintain Tickets<\/a><\/td><td class="num">1<\/td><td class="num"><span class="n-fail">1<\/span>/);
    });

    it('should offer a filter to show only the missed steps', () => {
      expect(page).toContain('id="missed-only"');
    });
  });

  describe('that has been written for a walk whose every step meets the intent', () => {
    it('should leave the scenario closed', () => {
      const page = readFileSync(writeWalkReport(new Run(runFolder([MEETS]).runDir)), 'utf8');
      expect(page).not.toMatch(/<details class="scenario failing"/);
    });
  });

  describe('that has been written for a step not judged yet', () => {
    it('should mark the step not judged', () => {
      const page = readFileSync(writeWalkReport(new Run(runFolder([{ ...MEETS, verdict: undefined, reason: undefined }]).runDir)), 'utf8');
      expect(page).toContain('<span class="check-name">Judge</span><span class="check-value">not judged</span>');
    });
  });

  describe('that has been written for a step run by a test that failed', () => {
    it("should show the test's failure among its checks", () => {
      const page = readFileSync(writeWalkReport(new Run(runFolder([{ ...MEETS, by: 'run by a test', result: 'fail' }]).runDir)), 'utf8');
      expect(page).toContain('<div class="check fail"><span class="check-name">Test</span><span class="check-value">failed</span></div>');
    });
  });

  describe('that has been written for the first run of its sub-epic', () => {
    it('should say there is no previous run to compare with', () => {
      const page = readFileSync(writeWalkReport(new Run(runFolder([MEETS]).runDir)), 'utf8');
      expect(page).toContain('<span class="check-name">Previous</span><span class="check-value">no previous run</span>');
    });
  });

  describe('that has been written for a run after a judged run', () => {
    let page: string;
    beforeEach(() => {
      const { root } = runFolder([MEETS, MISSES], 'run-1');
      const { runDir } = runFolder([{ ...MEETS, verdict: undefined, reason: undefined }, { ...MISSES, verdict: undefined, reason: undefined }], 'run-2', root);
      writeFileSync(path.join(runDir, THEN_SHOT), screenshot(128));
      page = readFileSync(writeWalkReport(new Run(runDir)), 'utf8');
    });

    it("should mark a step whose screen is the previous run's as the same", () => {
      expect(page).toContain('<span class="check-name">Previous</span><span class="check-value">same as run-1</span>');
    });

    it("should carry the previous run's verdict to a step whose screen has not changed", () => {
      expect(page).toContain('<span class="check-value">meets the intent · from run-1</span>');
    });

    it('should mark a step whose screen changed', () => {
      expect(page).toContain('<div class="check warn"><span class="check-name">Previous</span><span class="check-value">changed since run-1</span></div>');
    });

    it("should show a changed step's screen in the previous run beside its own, captioned with each run", () => {
      expect(page).toMatch(/<div class="shots"><figure class="shot"><a href="\.\.\/run-1\/screens\/maintain-tickets-rename-a-ticket-2-then\.png"[^]*?<figcaption>run-1<\/figcaption><\/figure><figure class="shot">[^]*?<figcaption>run-2<\/figcaption>/);
    });

    it('should say how much of the screen changed and where', () => {
      expect(page).toContain('What changed since run-1:</span> 100.00% of the screen across the whole screen');
    });

    it('should box the changed area in both screens', () => {
      expect(page.match(/<span class="change-box"/g)).toHaveLength(2);
    });

    it('should leave a step whose screen is the same with its one screen', () => {
      expect(page.match(/<div class="shots">/g)).toHaveLength(1);
    });

    it('should leave a changed step for the judge', () => {
      expect(page).toContain('<span class="check-name">Judge</span><span class="check-value">not judged</span>');
    });
  });

  describe('that has been written for a step whose screenshot is missing', () => {
    it('should say the step has no screenshot', () => {
      const page = readFileSync(writeWalkReport(new Run(runFolder([{ ...MEETS, screenshot: 'screens/gone.png' }]).runDir)), 'utf8');
      expect(page).toContain('no screenshot');
    });
  });

  describe('that has been written into the run history', () => {
    let historyDir: string;
    let page: string;
    beforeEach(() => {
      const { root, runDir } = runFolder([MEETS, MISSES]);
      historyDir = path.join(root, 'history', '2026-11-17');
      page = readFileSync(writeHistoryReport(new Run(runDir), historyDir, 'move-work-forward-on-session-board/maintain-tickets'), 'utf8');
    });

    it('should keep the page without its screenshots', () => {
      expect(page).not.toContain('<img data-shot=');
    });

    it('should add the missed step and its reason to the history summary', () => {
      expect(readFileSync(path.join(historyDir, 'summary.md'), 'utf8')).toContain('2 Then the card reads beta — misses the intent — The card still reads alpha');
    });
  });
});

describe('an end-to-end run compared with an accepted walk', () => {
  let root: string;
  let runDir: string;
  let walkDir: string;
  beforeEach(() => {
    ({ root, runDir: walkDir } = runFolder([MEETS, MISSES], 'walk-1'));
    const run = runFolder([{ ...MEETS, by: 'run by a test', result: 'pass', verdict: undefined }, { ...MISSES, by: 'run by a test', result: 'pass', verdict: undefined }], 'run-1', root);
    runDir = run.runDir;
  });

  describe('with a step whose screen is the same in both', () => {
    it('should mark the pair same', () => {
      expect(new Run(runDir).pairsAgainst(new Run(walkDir)).find(pair => pair.key === MEETS.key)?.change).toBe('same');
    });
  });

  describe('with a step whose screen differs', () => {
    it('should mark the pair changed', () => {
      writeFileSync(path.join(runDir, THEN_SHOT), screenshot(255));
      expect(new Run(runDir).pairsAgainst(new Run(walkDir)).find(pair => pair.key === MISSES.key)?.change).toBe('changed');
    });
  });

  describe('with a step the walk does not have', () => {
    it('should mark the pair new', () => {
      const extra: StepRow = { ...MEETS, key: `${STORY} › ${SCENARIO} › 3 And the card is still open`, step: 'And the card is still open' };
      writeFileSync(path.join(runDir, RESULTS_FILE), JSON.stringify([MEETS, MISSES, extra]));
      expect(new Run(runDir).pairsAgainst(new Run(walkDir)).find(pair => pair.key === extra.key)?.change).toBe('new');
    });
  });

  describe('that has its compare report written', () => {
    let page: string;
    beforeEach(() => {
      writeFileSync(path.join(runDir, THEN_SHOT), screenshot(255));
      page = readFileSync(writeCompareReport(new Run(runDir), new Run(walkDir)), 'utf8');
    });

    it("should show each step's two screens side by side, captioned with their runs", () => {
      expect(page).toContain('<figcaption>walk-1</figcaption>');
    });

    it("should link the walk's screen to its file in the walk's run folder", () => {
      expect(page).toContain('href="../walk-1/screens/maintain-tickets-rename-a-ticket-1-given.png"');
    });

    it('should mark the changed step', () => {
      expect(page).toMatch(/<span class="chip fail">changed \d/);
    });

    it('should count the pairs by how they changed', () => {
      expect(page).toContain('1 same · 1 changed · 0 new · 0 gone');
    });
  });
});

describe('the end-to-end story map report', () => {
  describe('with two runs of the same sub-epic', () => {
    let root: string;
    let page: string;
    beforeEach(() => {
      root = runFolder([MEETS, MISSES], 'walk-1').root;
      runFolder([MEETS], 'walk-2', root);
      page = readFileSync(writeStoryMapReport(root), 'utf8');
    });

    it('should be written at the root of the results', () => {
      expect(existsSync(path.join(root, 'story-map.html'))).toBe(true);
    });

    it("should link the sub-epic to its newest run's report", () => {
      expect(page).toContain('href="move-work-forward-on-session-board/maintain-tickets/walk-2/report.html#move-work-forward-on-session-board-maintain-tickets"');
    });

    it("should count the newest run's steps", () => {
      expect(page).toContain('1 meet · 0 miss');
    });
  });
});

describe('where a screen changed, in words', () => {
  it('should name the corner a small change sits in', () => {
    expect(placeOf({ left: 0.72, top: 0.94, width: 0.26, height: 0.04 })).toBe('in the bottom right');
  });

  it('should name the side of a change halfway down', () => {
    expect(placeOf({ left: 0.05, top: 0.4, width: 0.2, height: 0.2 })).toBe('on the left');
  });
});
