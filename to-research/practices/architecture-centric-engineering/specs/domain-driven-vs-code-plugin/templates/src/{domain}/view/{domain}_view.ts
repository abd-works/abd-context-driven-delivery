// src/{{domain}}/view/{{domain}}_view.ts
// Server view — extends BaseView; wraps domain; dispatches postMessage after mutations.
import type { WebviewPanel, Uri } from 'vscode';
import { BaseView } from '../../engine/base_view.js';
import type { I{{Domain}} } from '../{{domain}}.js';

export class {{Domain}}View extends BaseView implements I{{Domain}} {
  private _entity: I{{Domain}};
  readonly panel: WebviewPanel;

  constructor(panel: WebviewPanel, entity: I{{Domain}}, extensionUri: Uri) {
    super(extensionUri);
    this.panel = panel;
    this._entity = entity;
  }

  // TODO: implement each I{{Domain}} method; call postMessage after mutations
  // count(amount: number | string): void {
  //   this._entity.count(amount);
  //   this.panel.webview.postMessage({ total: this._entity.total });
  // }

  // reset(): void {
  //   this._entity.reset();
  //   this.panel.webview.postMessage({ total: this._entity.total });
  // }

  // get total(): number { return this._entity.total; }

  /** Map command strings to [target, method] for postMessage dispatch. */
  _lookup(pathStr: string): [object, string] {
    const routes: Record<string, [object, string]> = {
      // TODO: add routes for each command the webview can send
      // 'count': [this, 'count'],
      // 'reset': [this, 'reset'],
    };
    return routes[pathStr] ?? [this, pathStr];
  }

  getHtml(): string {
    return this.renderTemplate('{{domain}}/view/{{Domain}}.html', {
      // TODO: provide substitution values for the HTML template
    });
  }
}
