import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { PNG } from 'pngjs';
import { beforeEach, describe, expect, it } from 'vitest';
import { RESULTS_FILE, type StepRow, writeHistoryReport, writeStoryMapReport, writeWalkReport } from './report';

const STORY = 'Maintain Tickets';
const SCENARIO = 'Rename a ticket';
const GIVEN_SHOT = 'screens/maintain-tickets-rename-a-ticket-1-given.png';
const THEN_SHOT = 'screens/maintain-tickets-rename-a-ticket-2-then.png';

function screenshot(grey: number): Buffer {
  const image = new PNG({ width: 4, height: 4 });
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
      page = readFileSync(writeWalkReport(runFolder([MISSES, MEETS]).runDir), 'utf8');
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

    it("should show each step's verdict", () => {
      expect(page).toContain('<span class="chip fail">misses the intent</span>');
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
      const page = readFileSync(writeWalkReport(runFolder([MEETS]).runDir), 'utf8');
      expect(page).not.toMatch(/<details class="scenario failing"/);
    });
  });

  describe('that has been written for a step not judged yet', () => {
    it('should mark the step not judged', () => {
      const page = readFileSync(writeWalkReport(runFolder([{ ...MEETS, verdict: undefined, reason: undefined }]).runDir), 'utf8');
      expect(page).toContain('<span class="chip none">not judged</span>');
    });
  });

  describe('that has been written for a step run by a test that failed', () => {
    it("should show the test's failure beside the verdict", () => {
      const page = readFileSync(writeWalkReport(runFolder([{ ...MEETS, by: 'run by a test', result: 'fail' }]).runDir), 'utf8');
      expect(page).toContain('<span class="chip fail">test failed</span>');
    });
  });

  describe('that has been written for a step whose screenshot is missing', () => {
    it('should say the step has no screenshot', () => {
      const page = readFileSync(writeWalkReport(runFolder([{ ...MEETS, screenshot: 'screens/gone.png' }]).runDir), 'utf8');
      expect(page).toContain('no screenshot');
    });
  });

  describe('that has been written into the run history', () => {
    let historyDir: string;
    let page: string;
    beforeEach(() => {
      const { root, runDir } = runFolder([MEETS, MISSES]);
      historyDir = path.join(root, 'history', '2026-11-17');
      page = readFileSync(writeHistoryReport(runDir, historyDir, 'move-work-forward-on-session-board/maintain-tickets'), 'utf8');
    });

    it('should keep the page without its screenshots', () => {
      expect(page).not.toContain('<img data-shot=');
    });

    it('should add the missed step and its reason to the history summary', () => {
      expect(readFileSync(path.join(historyDir, 'summary.md'), 'utf8')).toContain('2 Then the card reads beta — misses the intent — The card still reads alpha');
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
