import React from 'react';
import { {{DomainName}}ListView } from '@{{appName}}/{{domainNames}}-client';

// Top-level view — composition of domain views.
// A top-level view can compose views from multiple domains.
// It owns layout and navigation between steps,
// but contains no domain logic of its own.
export function {{EpicName}}View() {
  return (
    <main className="{{epicSlug}}-page">
      <{{DomainName}}ListView />
    </main>
  );
}
