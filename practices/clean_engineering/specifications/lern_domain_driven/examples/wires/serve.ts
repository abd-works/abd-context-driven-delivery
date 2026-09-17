import { createApp } from './app';

const port = Number(process.env.PORT ?? 3001);
const app = await createApp();
app.listen(port, () => {
  console.log(`wires API listening on ${port}`);
});
