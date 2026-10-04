const db = { delete: (id: string) => id };
export function wipe(id: string) {
  db.delete(id);
}
