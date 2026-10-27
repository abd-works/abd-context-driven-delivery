export function handle(req: unknown) {
  return (req as any).user.id;
}
