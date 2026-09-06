// src/{{domain}}/{{domain}}_server.ts
// Server domain — extends the domain entity, adds file-based persistence.
import * as fs from 'fs';
import { {{Domain}} } from './{{domain}}.js';

export class {{Domain}}Server extends {{Domain}} {
  private _filePath: string;

  constructor(filePath: string) {
    super();
    this._filePath = filePath;
    this._load();
  }

  // TODO: override each mutation method to call this._save()
  // override count(amount: number | string): void {
  //   super.count(amount);
  //   this._save();
  // }

  // override reset(): void {
  //   super.reset();
  //   this._save();
  // }

  private _load(): void {
    if (!fs.existsSync(this._filePath)) return;
    const data = JSON.parse(fs.readFileSync(this._filePath, 'utf-8'));
    // TODO: restore state from data
    // if (typeof data.total === 'number') super.count(data.total);
  }

  private _save(): void {
    // TODO: serialize current state
    // fs.writeFileSync(this._filePath, JSON.stringify({ total: this.total }));
  }
}
