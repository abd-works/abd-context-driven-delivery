/**
 * {{domainName}}.ts — domain core (was shared/).
 *
 * Framework-free: no Express, no React, no lowdb. Schema, entity, collection,
 * and persistence interface live here once; {{domainName}}-server.ts and
 * {{domainName}}-client.tsx both import from this file (share-domain-logic).
 *
 * DDD: {{DomainName}} is the aggregate root. {{DomainName}}Repository is the
 * collection seam that load / create / search / update that root
 * (context_tools/ddd/ddd.md building_blocks).
 */
import { z } from 'zod';

export const {{DomainName}}Schema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1, '{{DomainName}} name is required').max(140),
  status: z.enum(['Active', 'Pending', 'Inactive']),
  createdAt: z.coerce.date(),
});

export const Create{{DomainName}}InputSchema = z.object({
  name: z.string().min(1, 'Name is required').max(140),
});

export type Create{{DomainName}}Input = {
  name: string;
};

export type {{DomainName}}Search = {
  status?: {{DomainName}}StatusType;
  name?: string;
};

export type {{DomainName}}DTO = {
  id: string;
  name: string;
  status: 'Active' | 'Pending' | 'Inactive';
  createdAt: Date;
};

export type {{DomainName}}StatusType = 'Active' | 'Pending' | 'Inactive';

export class {{DomainName}}Status {
  constructor(
    public readonly status: {{DomainName}}StatusType,
    public readonly createdAt: Date
  ) {}

  isActive(): boolean {
    return this.status === 'Active';
  }

  isPending(): boolean {
    return this.status === 'Pending';
  }
}

export class {{DomainName}} {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly status: {{DomainName}}Status,
    public readonly createdAt: Date,
  ) {}
}

/**
 * toDomainEntity — the one place a raw DTO becomes a real {{DomainName}}.
 * Both {{domainName}}-server.ts (repository boundary) and
 * {{domainName}}-client.tsx (HTTP boundary) call this (share-domain-logic).
 */
export function toDomainEntity(dto: {{DomainName}}DTO): {{DomainName}} {
  return new {{DomainName}}(
    dto.id,
    dto.name,
    new {{DomainName}}Status(dto.status, dto.createdAt),
    dto.createdAt,
  );
}

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

export interface {{DomainName}}Repository {
  load(id: string): Promise<{{DomainName}} | null>;
  create(input: Create{{DomainName}}Input): Promise<{{DomainName}}>;
  search(query?: {{DomainName}}Search): Promise<{{DomainName}}[]>;
  update(root: {{DomainName}}): Promise<{{DomainName}}>;
}
