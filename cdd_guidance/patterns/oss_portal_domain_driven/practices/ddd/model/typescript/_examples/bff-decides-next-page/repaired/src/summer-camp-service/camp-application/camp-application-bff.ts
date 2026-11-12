import { CampApplication } from './camp-application';
import { APPLIED_PATH } from './camp-application-paths';
export class CampApplicationBff extends CampApplication {
  destination() { return APPLIED_PATH; }
}
