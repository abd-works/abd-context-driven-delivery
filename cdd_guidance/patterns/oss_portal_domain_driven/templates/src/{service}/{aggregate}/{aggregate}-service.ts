// Runs in {service} on Cloud Run. Only {{Aggregate}}RepositorySql touches the service's own database (§3.5).
import { {{Aggregate}}, {{Aggregate}}Repository, {{Aggregate}}Submitted, {{aggregate}}Schema } from './{aggregate}';

export class {{Aggregate}}Service extends {{Aggregate}} {
  static async submit(id: string, repository: {{Aggregate}}RepositorySql, events: EventPublisher): Promise<{{Aggregate}}> {
    const root = await repository.load(id);
    if (root === null) throw new CatalogueError('{{AGGREGATE}}-404');
    const submitted = await repository.update(root.submit());
    await events.publish(new {{Aggregate}}Submitted(submitted.id)); // after the transaction commits (APP-07)
    return submitted;
  }
}

export class {{Aggregate}}RepositorySql extends {{Aggregate}}Repository {
  constructor(private readonly db: Database) { super(); }

  async load(id: string): Promise<{{Aggregate}} | null> {
    const found = await this.db.one('SELECT id, status FROM {{aggregate_table}} WHERE id = $1', [id]);
    return found ? Object.assign(new {{Aggregate}}(found.id), {{aggregate}}Schema.parse(found)) : null;
  }

  async update(root: {{Aggregate}}): Promise<{{Aggregate}}> {
    await this.db.run('UPDATE {{aggregate_table}} SET status = $1 WHERE id = $2', [root.status, root.id]);
    return root;
  }
}
