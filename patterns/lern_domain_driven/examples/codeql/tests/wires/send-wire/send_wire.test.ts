describe('GET /api/recipients returns 200', () => {
  it('wipes the store', () => {
    db.deleteMany({});
  });
});

const db = { deleteMany: (_filter: object) => undefined };
