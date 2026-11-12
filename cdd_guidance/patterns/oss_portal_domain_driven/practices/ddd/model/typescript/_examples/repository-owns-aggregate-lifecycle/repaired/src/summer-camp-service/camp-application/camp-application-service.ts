import { CampApplication, CampApplicationRepository } from './camp-application';
export class CampApplicationService extends CampApplication {
  async submit(repository: CampApplicationRepositorySql) { await repository.update(this.submitted()); }
}
export class CampApplicationRepositorySql extends CampApplicationRepository {
  async update(root: CampApplication) { await this.db.query('UPDATE camp_application SET status = $1 WHERE id = $2', [root.status, root.id]); return root; }
}
