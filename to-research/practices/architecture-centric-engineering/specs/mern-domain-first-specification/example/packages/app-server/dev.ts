import express from 'express';
import { createApp } from './app';

const app = createApp();

app.get('/health', (_req, res) => {
  res.json({ ok: true });
});

const port = 3001;
app.listen(port, () => {
  console.log(`API listening on http://localhost:${port}`);
});

export { app };
