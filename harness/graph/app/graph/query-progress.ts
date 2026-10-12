export type QueryStep = {
  index: number;
  total: number;
  name: string;
  phase: string;
};

export type QueryProgress = {
  headline: string;
  steps: QueryStep[];
  detail: string;
};

function queryName(path: string): string {
  const trimmed = path.trim().replace(/[.\s]+$/, '');
  const slash = Math.max(trimmed.lastIndexOf('/'), trimmed.lastIndexOf('\\'));
  return slash >= 0 ? trimmed.slice(slash + 1) : trimmed;
}

function statusText(line: string): string {
  return line.replace(/^(load|queries|query|codeql|error):\s*/, '').trim();
}

export function queryProgress(messages: string[]): QueryProgress {
  const steps: QueryStep[] = [];
  let current: QueryStep | null = null;
  let detail = '';
  let status = '';
  for (const line of messages) {
    if (line.includes('WARNING')) {
      continue;
    }
    const text = statusText(line);
    if (text) {
      status = text;
    }
    const compiled = line.match(/\[(\d+)\/(\d+)[^\]]*\]\s*Compiled\s+(.+)$/);
    if (compiled) {
      const step = {
        index: Number(compiled[1]),
        total: Number(compiled[2]),
        name: queryName(compiled[3]),
        phase: 'Compiled',
      };
      steps.push(step);
      current = step;
      detail = `${step.index}/${step.total} ${step.name}`;
      continue;
    }
    const plan = line.match(/Compiling query plan for\s+(.+)$/);
    if (plan) {
      const name = queryName(plan[1]);
      const total = current?.total ?? 0;
      const index = current ? current.index + (current.phase === 'Compiled' ? 1 : 0) : 1;
      current = { index, total, name, phase: 'Compiling' };
      detail = total ? `Compiling ${index}/${total} ${name}` : `Compiling ${name}`;
      continue;
    }
    const queued = line.match(/^query:\s*(\d+)\/(\d+)\s+(\S+)/);
    if (queued) {
      current = { index: Number(queued[1]), total: Number(queued[2]), name: queued[3], phase: 'Query' };
      detail = `${current.index}/${current.total} ${current.name}`;
      continue;
    }
    const started = line.match(/Starting evaluation of\s+(.+)$/);
    if (started) {
      const name = queryName(started[1]);
      current = {
        index: current?.index ?? 0,
        total: current?.total ?? 0,
        name,
        phase: 'Running',
      };
      detail = line.replace(/^codeql:\s*/, '');
      continue;
    }
    if (line.includes('.ql') || /^\(\d+%\)/.test(text)) {
      detail = text;
    }
  }
  const compiled = current
    ? `${current.phase} ${current.index}/${current.total} ${current.name}`.replace(' 0/0 ', ' ')
    : '';
  const headline = compiled
    ? detail.startsWith('(') ? `${compiled} ${detail}` : compiled
    : status || 'Loading the graph…';
  if (!detail) {
    detail = status;
  }
  const seen = new Set<string>();
  const unique = steps.filter((step) => {
    const key = `${step.index}:${step.name}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
  return { headline, steps: unique.slice(-120), detail };
}
