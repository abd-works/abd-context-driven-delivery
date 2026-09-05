/**
 * {{DomainName}}.ts — Entity and Value Objects for the {{domainName}} module.
 *
 * Replace '{{DomainName}}' with your entity (PascalCase).
 * This file lives in packages/{{domainNames}}/shared/ and has ZERO framework imports.
 */

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

export interface {{DomainName}} {
  id: string;
  name: string;
  status: {{DomainName}}Status;
  createdAt: Date;
}
