declare module 'express' {
  export interface Request {
    user?: { enterpriseId: string; token: string };
    query: Record<string, string | undefined>;
    params: Record<string, string>;
    body: any;
  }
  export interface Response {
    json(body: any): Response;
    status(code: number): Response;
  }
  export interface Router {
    get(path: string, handler: (req: Request, res: Response) => any): void;
    post(path: string, handler: (req: Request, res: Response) => any): void;
  }
  export function Router(): Router;
  export interface Application {
    use(path: string, handler: any): void;
    use(handler: any): void;
  }
  export default function express(): Application;
  export function json(): any;
}
