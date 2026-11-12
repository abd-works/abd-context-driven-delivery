import { CampApplication } from './camp-application';
export class CampApplicationClient extends CampApplication {
  submit(token: string) { return fetch('/bff/camp-applications', { headers: { Authorization: `Bearer ${token}` } }); }
}
