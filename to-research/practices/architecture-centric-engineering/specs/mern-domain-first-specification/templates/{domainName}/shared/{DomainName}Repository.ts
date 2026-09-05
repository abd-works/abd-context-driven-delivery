/**
 * {{DomainName}}Repository.ts — Repository interface (shared, framework-free).
 *
 * Server provides the concrete implementation.
 */
import { {{DomainName}} } from './{{DomainName}}';
import { Create{{DomainName}}Input } from './{{domainName}}.schema';

export interface {{DomainName}}Repository {
  findAll(): Promise<{{DomainName}}[]>;
  findById(id: string): Promise<{{DomainName}} | null>;
  save(input: Create{{DomainName}}Input): Promise<{{DomainName}}>;
}
