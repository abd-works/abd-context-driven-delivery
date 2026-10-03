import { createRecipientsRouter } from './recipient-server';

export function RecipientPage() {
  return createRecipientsRouter;
}

export async function fetchRecipients() {
  const data = await (await fetch('/api/recipients')).json();
  return data.recipients;
}
