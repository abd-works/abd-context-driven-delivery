import type { EngineInterface } from 'claude-code'

// Resolves to answer once milliseconds have passed on the engine's clock.
export function after($: EngineInterface, milliseconds: number, answer: string): Promise<string> {
  return new Promise(resolve => $.clock.after(milliseconds, () => resolve(answer)))
}
