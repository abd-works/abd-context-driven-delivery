// counter/counter_server.ts — server domain: implements ICounter via Counter, adds persistence
import { Counter } from "./counter.js";
import * as fs from "fs";

export class CounterServer extends Counter {
  private _filePath: string;

  constructor(filePath: string) {
    super();
    this._filePath = filePath;
    this._load();
  }

  private _load(): void {
    try {
      const data = JSON.parse(fs.readFileSync(this._filePath, "utf8"));
      this.hydrate(data);
    } catch (_) {
      // File doesn't exist or is invalid — start fresh
    }
  }

  private _save(): void {
    fs.writeFileSync(
      this._filePath,
      JSON.stringify({ total: this.total, fooBar: this.foo.bar })
    );
  }

  override count(amount: number | string): void {
    super.count(amount);
    this._save();
  }

  override reset(): void {
    super.reset();
    this._save();
  }
}
