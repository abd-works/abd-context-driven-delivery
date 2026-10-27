export class GuardError extends Error {}
export function fail(): never {
  throw new GuardError("blocked")
}
