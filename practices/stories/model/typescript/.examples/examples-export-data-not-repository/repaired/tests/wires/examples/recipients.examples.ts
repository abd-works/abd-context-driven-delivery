export function seedRecipient(repo: { seed: (row: object) => object }) {
  return repo.seed({ id: "1" });
}
