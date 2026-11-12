import { CampApplication } from './camp-application';
export class CampApplicationClient extends CampApplication {
  submit() { return fetch('/v1/summer-camp/camp-applications', { method: 'POST' }); }
}
