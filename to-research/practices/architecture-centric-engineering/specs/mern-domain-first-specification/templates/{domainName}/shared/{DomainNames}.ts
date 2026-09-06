/**
 * {{DomainName}}s.ts — Collection class with domain-oriented query methods.
 *
 * Wraps a {{DomainName}}[] array with fluent, chainable methods.
 * Used identically on client and server — same logic, zero duplication.
 */
import { {{DomainName}}, {{DomainName}}StatusType } from './{{DomainName}}';

export class {{DomainName}}s {
  constructor(private readonly items: {{DomainName}}[]) {}

  filterByStatus(status: {{DomainName}}StatusType): {{DomainName}}s {
    return new {{DomainName}}s(this.items.filter(r => r.status.status === status));
  }

  search(query: string): {{DomainName}}s {
    const lower = query.toLowerCase();
    return new {{DomainName}}s(
      this.items.filter(r => r.name.toLowerCase().includes(lower))
    );
  }

  toArray(): {{DomainName}}[] {
    return [...this.items];
  }

  get length(): number {
    return this.items.length;
  }
}
