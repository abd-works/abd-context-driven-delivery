import { CampApplication } from './camp-application';
import { APPLIED_PATH } from './camp-application-paths';
export class CampApplicationBff extends CampApplication {
  async submit() { await pubsub.topic('application-submitted').publishMessage({ json: { id: this.id } }); }
  destination() { return APPLIED_PATH; }
}
