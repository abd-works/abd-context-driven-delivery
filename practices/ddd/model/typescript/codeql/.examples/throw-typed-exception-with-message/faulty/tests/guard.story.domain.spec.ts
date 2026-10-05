export function fail(): never {
  throw { message: "blocked" }
}
