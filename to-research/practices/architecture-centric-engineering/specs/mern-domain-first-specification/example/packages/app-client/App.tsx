import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { HomeView } from './HomeView';
import { WirePaymentView } from './WirePaymentView';

// Composition root: React Router maps paths to top-level views.
// Top-level views compose domain views from one or more domain packages.
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeView />} />
      <Route path="/wire-payment/create" element={<WirePaymentView />} />
    </Routes>
  );
}
