// The headline a load shows until the cdd server reports a step of it.
export const LOADING_GRAPH = 'Loading the graph…';

type QueryStep = {
  index: number;
  total: number;
  name: string;
  phase: string;
};

export type QueryProgress = {
  headline: string;
  steps: QueryStep[];
  detail: string;
  index: number;
  total: number;
};

function queryName(path: string): string {
  const trimmed = path.trim().replace(/[.\s]+$/, '');
  const slash = Math.max(trimmed.lastIndexOf('/'), trimmed.lastIndexOf('\\'));
  return slash >= 0 ? trimmed.slice(slash + 1) : trimmed;
}

function statusText(line: string): string {
  return line.replace(/^(load|queries|query|error):\s*/, '').trim();
}

// How many compiled steps the progress keeps, the newest.
const STEPS_KEPT = 120;

// One read of the server's progress lines, line by line: the steps compiled so far, the step it is on, and the status
// and fraction it last reported.
class ProgressReading {
  private readonly steps: QueryStep[] = [];
  private current: QueryStep | null = null;
  private detail = '';
  private status = '';
  private index = 0;
  private total = 0;

  read(line: string): void {
    if (line.includes('WARNING')) return;
    const text = statusText(line);
    if (text) this.readStatus(text);
    if (this.readCompiled(line) || this.readPlan(line) || this.readQueued(line) || this.readStarted(line, text)) return;
    if (/^\(\d+%\)/.test(text)) this.detail = text;
  }

  get progress(): QueryProgress {
    const current = this.current;
    const compiled = current ? `${current.phase} ${current.index}/${current.total} ${current.name}`.replace(' 0/0 ', ' ') : '';
    const headline = compiled ? (this.detail.startsWith('(') ? `${compiled} ${this.detail}` : compiled) : this.status || LOADING_GRAPH;
    return { headline, steps: this.uniqueSteps().slice(-STEPS_KEPT), detail: this.detail || this.status, index: this.index, total: this.total };
  }

  private readStatus(text: string): void {
    this.status = text;
    const fraction = text.match(/(\d+)\/(\d+)/);
    if (fraction) {
      this.index = Number(fraction[1]);
      this.total = Number(fraction[2]);
    }
  }

  private readCompiled(line: string): boolean {
    const compiled = line.match(/\[(\d+)\/(\d+)[^\]]*\]\s*Compiled\s+(.+)$/);
    if (!compiled) return false;
    const step = { index: Number(compiled[1]), total: Number(compiled[2]), name: queryName(compiled[3]), phase: 'Compiled' };
    this.steps.push(step);
    this.current = step;
    this.detail = `${step.index}/${step.total} ${step.name}`;
    return true;
  }

  private readPlan(line: string): boolean {
    const plan = line.match(/Compiling query plan for\s+(.+)$/);
    if (!plan) return false;
    const name = queryName(plan[1]);
    const total: number = this.current?.total ?? 0;
    const index: number = this.current ? this.current.index + (this.current.phase === 'Compiled' ? 1 : 0) : 1;
    this.current = { index, total, name, phase: 'Compiling' };
    this.detail = total ? `Compiling ${index}/${total} ${name}` : `Compiling ${name}`;
    return true;
  }

  private readQueued(line: string): boolean {
    const queued = line.match(/^query:\s*(\d+)\/(\d+)\s+(\S+)/);
    if (!queued) return false;
    this.current = { index: Number(queued[1]), total: Number(queued[2]), name: queued[3], phase: 'Query' };
    this.detail = `${this.current.index}/${this.current.total} ${this.current.name}`;
    return true;
  }

  private readStarted(line: string, text: string): boolean {
    const started = line.match(/Starting evaluation of\s+(.+)$/);
    if (!started) return false;
    this.current = { index: this.current?.index ?? 0, total: this.current?.total ?? 0, name: queryName(started[1]), phase: 'Running' };
    this.detail = text;
    return true;
  }

  // Each compiled step once, at the first place it was compiled.
  private uniqueSteps(): QueryStep[] {
    const seen = new Set<string>();
    return this.steps.filter((step) => {
      const key = `${step.index}:${step.name}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }
}

export function queryProgress(messages: string[]): QueryProgress {
  const reading = new ProgressReading();
  for (const line of messages) reading.read(line);
  return reading.progress;
}
