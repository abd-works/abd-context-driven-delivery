declare module 'react-router-dom' {
  export function Route(props: { path: string; element: any }): any;
  export function Routes(props: { children: any }): any;
  export function Link(props: { to: string; children: any }): any;
  export function BrowserRouter(props: { children: any }): any;
}
