/**
 * serve.ts — Node process entry. Binds the feature's Express app to a port.
 */
import { createApp } from './app';

const port = Number(process.env.PORT ?? 3001);
createApp().listen(port, () => {
  console.log(`{{epicSlug}} API listening on ${port}`);
});
