// {{Aggregate}} — the aggregate root, its events, and the in-memory repository. Framework-free: every tier imports it.
import { z } from 'zod';

export const {{aggregate}}Schema = z.object({ id: z.string(), status: z.enum(['draft', 'submitted']) });

export class {{Aggregate}} {
  constructor(readonly id: string, readonly status: 'draft' | 'submitted' = 'draft') {}

  submit(): {{Aggregate}} {
    return new {{Aggregate}}(this.id, 'submitted');
  }
}

export class {{Aggregate}}Submitted {
  constructor(readonly {{aggregate}}Id: string) {}
}

export class {{Aggregate}}Repository {
  protected roots = new Map<string, {{Aggregate}}>();
  async load(id: string): Promise<{{Aggregate}} | null> { return this.roots.get(id) ?? null; }
  async create(root: {{Aggregate}}): Promise<{{Aggregate}}> { this.roots.set(root.id, root); return root; }
  async search(): Promise<{{Aggregate}}[]> { return [...this.roots.values()]; }
  async update(root: {{Aggregate}}): Promise<{{Aggregate}}> { this.roots.set(root.id, root); return root; }
}
