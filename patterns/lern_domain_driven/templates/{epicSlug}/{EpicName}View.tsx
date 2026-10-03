import React from 'react';
import { {{DomainName}}ListView } from './{{domainName}}/{{domainName}}-client';

/**
 * {{EpicName}}View — feature view for the {{epicSlug}} package.
 *
 * Composes domain views from nested domain modules
 * ({{epicSlug}}/{{domainName}}/) — no domain logic of its own. The feature
 * package also owns process boot (`app.ts`, `main.tsx`).
 */
export function {{EpicName}}View() {
  return (
    <main className="{{epicSlug}}-page">
      <{{DomainName}}ListView />
    </main>
  );
}
