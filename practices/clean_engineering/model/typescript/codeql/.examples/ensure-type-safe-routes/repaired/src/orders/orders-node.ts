type Authed = { user: { id: string } };
export function handle(req: Authed) {
  return req.user.id;
}
