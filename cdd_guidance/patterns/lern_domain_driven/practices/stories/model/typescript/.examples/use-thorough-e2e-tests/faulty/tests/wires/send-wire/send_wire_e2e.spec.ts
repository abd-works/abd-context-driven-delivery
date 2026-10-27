const db = { deleteMany: (_filter: object) => undefined };
export function wipe() {
  db.deleteMany({});
}
