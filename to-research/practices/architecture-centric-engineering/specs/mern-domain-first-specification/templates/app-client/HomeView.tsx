import React from 'react';
import { Link } from 'react-router-dom';

export function HomeView() {
  return (
    <main className="home-view">
      <h1>{{appName}}</h1>
      <nav>
        <Link to="/{{epicSlug}}">{{EpicName}}</Link>
      </nav>
    </main>
  );
}
