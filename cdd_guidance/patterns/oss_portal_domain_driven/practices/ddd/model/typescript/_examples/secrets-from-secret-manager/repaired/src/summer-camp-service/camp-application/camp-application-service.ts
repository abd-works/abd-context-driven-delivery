import { CampApplication } from './camp-application';
const password = await secrets.access('camp-db-password');
export class CampApplicationService extends CampApplication {}
