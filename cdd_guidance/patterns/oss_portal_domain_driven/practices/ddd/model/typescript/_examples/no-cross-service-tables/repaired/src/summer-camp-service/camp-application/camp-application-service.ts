import { CampApplication } from './camp-application';
import { identityGateway } from '../summer-camp-service-gateways';
export class CampApplicationService extends CampApplication {
  guardianOf(id: string) { return identityGateway.get(`/v1/identity/profiles/${id}`); }
}
