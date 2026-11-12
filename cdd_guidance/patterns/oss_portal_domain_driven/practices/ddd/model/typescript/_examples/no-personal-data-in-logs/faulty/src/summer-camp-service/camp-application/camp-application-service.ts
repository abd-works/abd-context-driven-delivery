import { CampApplication } from './camp-application';
export class CampApplicationService extends CampApplication {
  submit() { logger.info('application submitted', this.applicant.email); }
}
