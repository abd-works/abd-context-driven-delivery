// The browser client the views render. It calls only the BFF, on the portal's own origin, with the session cookie.
import { {{Aggregate}} } from './{aggregate}';

export class {{Aggregate}}Client extends {{Aggregate}} {
  async submitOnServer(): Promise<string> {
    const answer = await fetch(`/bff/{{aggregates}}/${this.id}/submit`, { method: 'POST', credentials: 'same-origin' });
    return (await answer.json()).destination;
  }
}
