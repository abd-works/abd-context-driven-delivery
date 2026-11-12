import { CampApplication } from './camp-application';
import { APPLIED_PATH } from './camp-application-paths';
export class CampApplicationBff extends CampApplication {
  async submit() { await this.gateway.post(`/v1/summer-camp/camp-applications/${this.id}/submit`); }
  destination() { return APPLIED_PATH; }
}
