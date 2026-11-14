// Runs in the Node SSR server of citizen-portal-app. The token stays here, in the session (§3.2).
import { {{Aggregate}} } from './{aggregate}';
import { SUBMITTED_PATH } from './{aggregate}-paths';

export class {{Aggregate}}Gateway {
  constructor(private readonly session: PortalSession) {}
  submit(id: string): Promise<{ id: string; status: string }> {
    return this.session.callGateway('POST', `/v1/{{serviceBasePath}}/{{aggregates}}/${id}/submit`);
  }
}

export class {{Aggregate}}Bff extends {{Aggregate}} {
  static async submit(id: string, gateway: {{Aggregate}}Gateway): Promise<{{Aggregate}}Bff> {
    const answer = await gateway.submit(id);
    return new {{Aggregate}}Bff(answer.id, answer.status === 'submitted' ? 'submitted' : 'draft');
  }

  destination(): string {
    return SUBMITTED_PATH;
  }
}
