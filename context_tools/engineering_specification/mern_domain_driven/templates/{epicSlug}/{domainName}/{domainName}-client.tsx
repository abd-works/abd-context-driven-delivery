/**
 * {{domainName}}-client.tsx — client tier for the {{domainName}} domain.
 *
 * HTTP boundary, React hook, and views — one file. Must be `.tsx` because it
 * contains JSX. Browser-only; never imported from {{domainName}}-server.ts
 * (maintain-layer-purity).
 */
import { useState, useEffect, useCallback } from 'react';
import {
  {{DomainName}},
  {{DomainName}}s,
  {{DomainName}}Schema,
  toDomainEntity,
} from './{{domainName}}';

const API_BASE = '/api/{{domainNames}}';

export async function list{{DomainName}}s(
  filters?: { activeOnly?: boolean }
): Promise<{{DomainName}}[]> {
  const params = new URLSearchParams();
  if (filters?.activeOnly) params.set('active_only', 'true');
  const response = await fetch(`${API_BASE}?${params}`);
  const data = await response.json();
  return data.map((raw: unknown) => toDomainEntity({{DomainName}}Schema.parse(raw)));
}

export async function get{{DomainName}}(id: string): Promise<{{DomainName}}> {
  const response = await fetch(`${API_BASE}/${id}`);
  const data = await response.json();
  return toDomainEntity({{DomainName}}Schema.parse(data));
}

export async function create{{DomainName}}(
  input: Record<string, unknown>
): Promise<{{DomainName}}> {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  });
  const data = await response.json();
  return toDomainEntity({{DomainName}}Schema.parse(data));
}

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

interface {{DomainName}}CardViewProps {
  item: {{DomainName}};
  onSelect?: (item: {{DomainName}}) => void;
}

export function {{DomainName}}CardView({ item, onSelect }: {{DomainName}}CardViewProps) {
  return (
    <div
      className="{{domainName}}-card"
      onClick={() => onSelect?.(item)}
      role={onSelect ? 'button' : undefined}
    >
      <h3>{item.name}</h3>
      <span className="status">{item.status.status}</span>
    </div>
  );
}

interface {{DomainName}}ListViewProps {
  onSelectItem?: (item: {{DomainName}}) => void;
}

export function {{DomainName}}ListView({ onSelectItem }: {{DomainName}}ListViewProps) {
  const { items, loading, filterBySearch } = use{{DomainName}}s();
  const [searchQuery, setSearchQuery] = useState('');

  const displayed = searchQuery ? filterBySearch(searchQuery) : items;

  if (loading) return <p>Loading...</p>;

  return (
    <div className="{{domainName}}-list">
      <input
        type="search"
        placeholder="Search..."
        value={searchQuery}
        onChange={(e: any) => setSearchQuery(e.target.value)}
      />
      {displayed.map(item => (
        <{{DomainName}}CardView key={item.id} item={item} onSelect={onSelectItem} />
      ))}
    </div>
  );
}
