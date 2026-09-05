declare module 'react' {
  export function useState<T>(initial: T | (() => T)): [T, (v: T | ((prev: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useCallback<T extends (...args: any[]) => any>(fn: T, deps: any[]): T;
  export type ReactNode = any;
  export type FC<P = {}> = (props: P) => ReactNode;
  const React: any;
  export default React;
}
