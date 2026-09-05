// src/engine/engine.ts
// Composition root domain — holds named domain instances; no platform imports.
import type { I{{Domain}} } from '../{{domain}}/{{domain}}.js';
// TODO: import additional domain types as needed

export class Engine {
  private _instances: Map<string, I{{Domain}}> = new Map();

  add(name: string, instance: I{{Domain}}): void {
    this._instances.set(name, instance);
  }

  get(name: string): I{{Domain}} | undefined {
    return this._instances.get(name);
  }

  // TODO: add domain methods that compose across instances
}
