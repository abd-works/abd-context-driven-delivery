/**
 * {{domainName}}.repository.ts — MongoDB data access for the domain entity.
 *
 * Validates raw documents with the shared Zod schema at the repository
 * boundary, ensuring only typed domain entities propagate through the system.
 */
import { Collection, Db } from 'mongodb';
import { {{DomainName}}, {{DomainName}}Status, {{DomainName}}Schema, {{DomainName}}DTO, Create{{DomainName}}Input } from '@{{appName}}/{{domainNames}}-shared';

function toDomainEntity(dto: {{DomainName}}DTO): {{DomainName}} {
  return {
    id: dto.id,
    name: dto.name,
    status: new {{DomainName}}Status(dto.status, dto.createdAt),
    createdAt: dto.createdAt,
  };
}

export class {{DomainName}}sRepository {
  private collection: Collection;

  constructor(db: Db) {
    this.collection = db.collection('{{domainNames}}');
  }

  async findAll(): Promise<{{DomainName}}[]> {
    const docs = await this.collection.find().toArray();
    return docs.map(doc => toDomainEntity({{DomainName}}Schema.parse(doc)));
  }

  async findById(id: string): Promise<{{DomainName}} | null> {
    const doc = await this.collection.findOne({ id });
    if (!doc) return null;
    return toDomainEntity({{DomainName}}Schema.parse(doc));
  }

  async save(input: Create{{DomainName}}Input): Promise<{{DomainName}}> {
    const doc = {
      id: crypto.randomUUID(),
      name: input.name,
      status: 'Pending',
      createdAt: new Date(),
    };
    await this.collection.insertOne(doc);
    return toDomainEntity({{DomainName}}Schema.parse(doc));
  }
}
