import React from 'react';
import { createRoot } from 'react-dom/client';
import { WirePaymentView } from './WirePaymentView';

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WirePaymentView />
  </React.StrictMode>,
);
