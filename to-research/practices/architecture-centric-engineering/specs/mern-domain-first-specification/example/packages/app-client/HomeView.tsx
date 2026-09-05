import React from 'react';
import { Link } from 'react-router-dom';

export function HomeView() {
  return (
    <main className="home-view">
      <h1>Wire Payment Example</h1>
      <nav>
        <Link to="/wire-payment/create">Create Wire Payment</Link>
      </nav>
    </main>
  );
}
