/**
 * {{DomainName}}ListView.tsx — Container component with search and list rendering.
 */
import { useState } from 'react';
import { {{DomainName}} } from '@{{appName}}/{{domainNames}}-shared';
import { use{{DomainName}}s } from './use{{DomainName}}s';
import { {{DomainName}}CardView } from './{{DomainName}}CardView';

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
