export function send(res: { json: (body: object) => void }) {
  res.json({ success: true });
}
