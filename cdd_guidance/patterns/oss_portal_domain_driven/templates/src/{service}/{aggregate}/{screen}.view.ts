// Renders the client it holds with Government Design System components; it fetches nothing itself (APP-09 step 5).
import { Component, Input } from '@angular/core';
import { {{Aggregate}}Client } from './{aggregate}-client';

@Component({
  selector: 'oss-{screen}',
  standalone: true,
  template: `<gds-button (click)="submit()">{{ content('{screen}.submit') }}</gds-button>`,
})
export class {{Screen}}View {
  @Input({ required: true }) client!: {{Aggregate}}Client;
  @Input({ required: true }) content!: (key: string) => string; // wording from system-config-service (APP-03)
  @Input({ required: true }) navigate!: (path: string) => void;

  async submit(): Promise<void> {
    this.navigate(await this.client.submitOnServer());
  }
}
