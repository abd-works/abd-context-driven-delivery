import { CampApplication, CampApplicationRepository } from './camp-application';
export class CampApplicationService extends CampApplication {
  async submit(db: Db) { await db.query('UPDATE camp_application SET status = $1 WHERE id = $2', ['submitted', this.id]); }
}
export class CampApplicationRepositorySql extends CampApplicationRepository {}
