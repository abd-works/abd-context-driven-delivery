declare module 'vitest' {
  export function describe(name: string, fn: () => void): void;
  export function it(name: string, fn: () => Promise<void> | void): void;
  export function beforeEach(fn: () => Promise<void> | void): void;
  export function afterEach(fn: () => Promise<void> | void): void;
  export function expect(value: any): any;
}
declare module 'vitest/config' {
  export function defineConfig(config: any): any;
}
