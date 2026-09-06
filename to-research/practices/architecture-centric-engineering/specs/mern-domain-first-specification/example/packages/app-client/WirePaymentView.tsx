import React from 'react';
import { RecipientListView } from '@channelone/recipients-client';

// Top-level view — composition of domain views.
// A top-level view can compose views from multiple domains.
// It owns layout and navigation between steps,
// but contains no domain logic of its own.
export function WirePaymentView() {
  return (
    <main className="wire-payment-page">
      <RecipientListView />
      {/* Step 2, Step 3, etc. composed here as the flow grows */}
    </main>
  );
}
