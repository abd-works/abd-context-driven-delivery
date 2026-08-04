import { RecipientListView } from './recipients/recipient-client';

/**
 * WirePaymentView - feature view for the wires package.
 *
 * Composes domain views from nested `recipients/` — no domain logic of its
 * own. The feature package also owns process boot (`app.ts`, `main.tsx`).
 */
export function WirePaymentView() {
  return (
    <main className="wire-payment-page">
      <RecipientListView />
    </main>
  );
}
