declare module 'react-dom/client' {
  export function createRoot(el: HTMLElement): { render(node: any): void };
}
declare module 'react-dom' {
  export * from 'react-dom/client';
}
