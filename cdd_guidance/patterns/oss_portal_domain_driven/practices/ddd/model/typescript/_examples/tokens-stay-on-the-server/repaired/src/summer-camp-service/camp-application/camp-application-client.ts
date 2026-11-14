import { CampApplication } from './camp-application';
export class CampApplicationClient extends CampApplication {
  submit() { return fetch('/bff/camp-applications', { credentials: 'same-origin' }); }
}
