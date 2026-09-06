// counter/view/counter_view.ts — Server view: implements ICounter, delegates to domain, posts to webview
import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";
import { BaseView } from "../../engine/base_view";
import type { ICounter, IFoo } from "../counter";

export class CounterView extends BaseView implements ICounter {
  /** Raw template HTML. View loads and stores; tests use for DOM fixtures. Single source of truth. */
  static get template(): string {
    if (!(CounterView as { _template?: string })._template) {
      const p = path.join(__dirname, "Counter.html");
      (CounterView as { _template?: string })._template = fs.readFileSync(
        p,
        "utf8"
      );
    }
    return (CounterView as { _template?: string })._template!;
  }

  private _panel: vscode.WebviewPanel;
  private _counter: ICounter;
  foo: IFoo;

  constructor(
    panel: vscode.WebviewPanel,
    counter: ICounter,
    extensionUri: vscode.Uri
  ) {
    super(extensionUri);
    this._panel = panel;
    this._counter = counter;

    const v = this;
    this.foo = {
      get bar(): string {
        return v._counter.foo.bar;
      },
      set bar(val: string) {
        v._counter.foo.bar = val;
        v._panel.webview.postMessage({ fooBar: val });
      },
    };
  }

  get total(): number {
    return this._counter.total;
  }

  getHtml(): string {
    const counterCssUri = this._panel.webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "dist", "counter", "view", "counter.css")
    );
    return this.renderTemplate("dist/counter/view/Counter.html", {
      total: String(this._counter.total),
      fooBar: this._counter.foo?.bar ?? "",
      counterCssUri: counterCssUri.toString(),
    });
  }

  count(amount: number | string): void {
    this._counter.count(amount);
    this._panel.webview.postMessage({ total: this._counter.total });
  }

  reset(): void {
    this._counter.reset();
    this._panel.webview.postMessage({ total: this._counter.total });
  }

  hydrate(data: { total?: number; fooBar?: string }): void {
    this._counter.hydrate?.(data);
  }
}
