/**
 * use{{DomainName}}s.ts — React hook for domain entity state management.
 *
 * Loads domain entities from the API and exposes search/filter using
 * the SHARED {{DomainName}}s collection class — same logic as server-side.
 */
import { useState, useEffect, useCallback } from 'react';
import { {{DomainName}}, {{DomainName}}s } from '@{{appName}}/{{domainNames}}-shared';
import { list{{DomainName}}s } from './{{domainName}}.api';

export function use{{DomainName}}s() {
  const [items, setItems] = useState<{{DomainName}}[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    list{{DomainName}}s({ activeOnly: true })
      .then(setItems)
      .finally(() => setLoading(false));
  }, []);

  const filterBySearch = useCallback((query: string) => {
    const collection = new {{DomainName}}s(items);
    return collection.search(query).toArray();
  }, [items]);

  return { items, loading, filterBySearch };
}
