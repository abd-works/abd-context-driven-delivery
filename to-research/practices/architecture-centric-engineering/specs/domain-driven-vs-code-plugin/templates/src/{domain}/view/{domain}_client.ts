// src/{{domain}}/view/{{domain}}_client.ts
// Client DOM adapter — runs in the webview; implements I{{Domain}} with DOM bindings.
// Bundled by esbuild/webpack; shares the domain class with the extension host.
import { {{Domain}} } from '../{{domain}}.js';
import type { I{{Domain}} } from '../{{domain}}.js';

export function init{{Domain}}Client(vscode: { postMessage(msg: unknown): void }): I{{Domain}} {
  const entity = new {{Domain}}();   // same class bundled into the webview

  function syncToServer(): void {
    // TODO: post mutations back to extension host
    // vscode.postMessage({ command: 'count', args: [entity.total] });
  }

  const dom{{Domain}}: I{{Domain}} = {
    // TODO: implement each method — update DOM, sync to server
    // count(amount) {
    //   entity.count(amount);
    //   document.getElementById('total')!.textContent = String(entity.total);
    //   syncToServer();
    // },
    // reset() {
    //   entity.reset();
    //   document.getElementById('total')!.textContent = '0';
    //   syncToServer();
    // },
    // get total() { return entity.total; },
  } as unknown as I{{Domain}};

  window.addEventListener('message', (event) => {
    // TODO: reconcile server state to client display
    // const { total } = event.data as { total: number };
    // entity.count(total - entity.total);
    // document.getElementById('total')!.textContent = String(total);
  });

  return dom{{Domain}};
}
