/**
 * {{DomainName}}CardView.tsx — Presentational component for a single domain entity.
 */
import { {{DomainName}} } from '@{{appName}}/{{domainNames}}-shared';

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
