// counter/view/counter_client.ts — Client: extends Counter with DOM updates and server sync

import { Counter, type HydrateData } from "../counter.js";

interface VsCodeApi {
  postMessage(message: unknown): void;
}

/** Extends Counter with DOM updates and server synchronization */
export class CounterClient extends Counter {
  private vscode: VsCodeApi;
  private totalEl: HTMLSpanElement;
  private fooBarInput: HTMLInputElement;
  private amountInput: HTMLInputElement;

  constructor(vscode: VsCodeApi) {
    super();
    this.vscode = vscode;
    this.totalEl = document.getElementById("total") as HTMLSpanElement;
    this.amountInput = document.getElementById("amount") as HTMLInputElement;
    this.fooBarInput = document.getElementById("fooBar") as HTMLInputElement;
  }

  // TODO: make sure this is async
  private syncToServer(command: string, value?: unknown): void {
    this.vscode.postMessage(value !== undefined ? { command, value } : { command });
  }

  override count(amount: number | string): void {
    super.count(amount);
    this.totalEl.textContent = String(this.total);
    this.syncToServer("counter.count", Number(amount) || 0);    
  }

  override reset(): void {
    super.reset();
    this.totalEl.textContent = String(this.total);
    this.amountInput.value = "0";
    this.syncToServer("counter.reset");
  }

  setFooBar(val: string): void {
    this.foo.bar = val;
    this.fooBarInput.value = val;
    this.syncToServer("counter.foo.bar", val);
  }

  override hydrate(data: HydrateData): void {
    super.hydrate(data);
    if (data.total !== undefined) this.totalEl.textContent = String(this.total);
    if (data.fooBar !== undefined) this.fooBarInput.value = this.foo.bar;
  }
}

export function initCounterClient(vscode: VsCodeApi): CounterClient {
  const amountInput = document.getElementById("amount") as HTMLInputElement;
  const resetBtn = document.getElementById("resetBtn") as HTMLButtonElement;
  const fooBarInput = document.getElementById("fooBar") as HTMLInputElement;

  const counter = new CounterClient(vscode);

  amountInput.addEventListener("change", () => counter.count(amountInput.value));
  resetBtn.addEventListener("click", () => counter.reset());
  fooBarInput.addEventListener("change", () => counter.setFooBar(fooBarInput.value));

  window.addEventListener("message", (event: MessageEvent) => {
    if ("total" in event.data || "fooBar" in event.data) {
      counter.hydrate(event.data as HydrateData);
    }
  });

  // Request initial state from server
  vscode.postMessage({ command: "counter.total" });
  vscode.postMessage({ command: "counter.foo.bar" });

  return counter;
}
