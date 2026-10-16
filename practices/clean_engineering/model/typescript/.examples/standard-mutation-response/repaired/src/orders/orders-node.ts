export function send(res: { json: (body: object) => void }, order: object) {
  res.json(order);
}
