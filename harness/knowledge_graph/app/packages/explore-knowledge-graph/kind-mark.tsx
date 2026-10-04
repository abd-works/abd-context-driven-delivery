export function kindLabel(kind: string, isFile: boolean): string {
  if (isFile && kind === 'Module') {
    return 'File';
  }
  if (kind === 'FieldGroup') {
    return 'properties';
  }
  if (kind === 'OoadClass') {
    return 'Class';
  }
  if (kind === 'SubEpic') {
    return 'Sub-epic';
  }
  if (kind === 'BoundedContext') {
    return 'Bounded context';
  }
  if (kind === 'EntityRoot') {
    return 'Entity root';
  }
  if (kind === 'ValueObject') {
    return 'Value object';
  }
  if (kind === 'DomainEvent') {
    return 'Domain event';
  }
  if (kind === 'DomainService') {
    return 'Domain service';
  }
  return kind || 'Node';
}

const KNOWN_MARKS = new Set([
  'PracticeGraph',
  'File',
  'Module',
  'Package',
  'Class',
  'Operation',
  'Rule',
  'Rules',
  'Properties',
  'Relationships',
  'Relationship',
  'Book',
  'Gear',
  'Entity diagram',
  'Form',
  'Checklist',
  'Practice',
  'Epic',
  'Sub-epic',
  'Story',
  'Background',
  'Scenario',
  'Step',
  'Example',
  'Bounded context',
  'Aggregate',
  'Entity',
  'Entity root',
  'Value object',
  'Repository',
  'Domain event',
  'Domain service',
  'Specification',
  'Description',
  'Context',
  'Observation',
]);

export function KindMark({ kind, isFile }: { kind: string; isFile: boolean }) {
  const label = kindLabel(kind, isFile);
  return (
    <svg
      className="kind-mark"
      viewBox="0 0 16 16"
      width="16"
      height="16"
      data-kind={label}
      aria-label={label}
      role="img"
    >
      <title>{label}</title>
      {label === 'PracticeGraph' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <circle cx="8" cy="3.5" r="1.75" />
          <circle cx="3.5" cy="12" r="1.75" />
          <circle cx="12.5" cy="12" r="1.75" />
          <path d="M8 5.3v2.2L4.8 10.6M8 7.5l3.2 3.1" />
        </g>
      )}
      {label === 'File' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M5 2.5h4.2L12 5.3V13.5H5z" />
          <path d="M9.2 2.5V5.3H12" />
        </g>
      )}
      {label === 'Module' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M2.5 13V5.5h4.2l1.3 1.5H13.5V13z" />
        </g>
      )}
      {label === 'Class' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <rect x="3" y="3" width="10" height="10" rx="0.5" />
          <path d="M3 6.5h10" />
        </g>
      )}
      {label === 'Operation' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M5 4.5 2.5 8 5 11.5M11 4.5 13.5 8 11 11.5" />
        </g>
      )}
      {label === 'Rules' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M3.5 2.5h8v10L7.5 10.5 3.5 12.5z" />
        </g>
      )}
      {label === 'Rule' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <path d="M4 2.5h8v11.5L8 11.5 4 14z" />
        </g>
      )}
      {label === 'Properties' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        >
          <rect x="3" y="3.5" width="10" height="9" rx="1" />
          <path d="M5.5 6.5h5M5.5 9.5h3.5" />
        </g>
      )}
      {label === 'Relationships' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        >
          <circle cx="4" cy="8" r="2" />
          <circle cx="12" cy="8" r="2" />
          <path d="M6 8h4" />
        </g>
      )}
      {label === 'Relationship' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
        >
          <path d="M3 8h10M11 5.5 13.5 8 11 10.5" />
        </g>
      )}
      {label === 'Book' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M3.2 3.2h6.2A2.2 2.2 0 0 1 11.6 5.4V13H5.2A2 2 0 0 0 3.2 15z" />
          <path d="M3.2 3.2V15" />
        </g>
      )}
      {label === 'Gear' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
          <circle cx="8" cy="8" r="2.1" />
          <path d="M8 2.4v1.8M8 11.8v1.8M2.4 8h1.8M11.8 8h1.8M4.1 4.1l1.3 1.3M10.6 10.6l1.3 1.3M11.9 4.1 10.6 5.4M5.4 10.6 4.1 11.9" />
        </g>
      )}
      {label === 'Entity diagram' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.2">
          <rect x="1.4" y="1.6" width="4.2" height="3" />
          <rect x="10.4" y="1.6" width="4.2" height="3" />
          <rect x="5.9" y="11.2" width="4.2" height="3" />
          <path d="M5.6 3.1h4.8M8 4.6v6.6" />
        </g>
      )}
      {label === 'Form' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="2.4" width="10" height="11.2" rx="1" />
          <path d="M5.2 6h5.6M5.2 8.6h5.6M5.2 11.2h3" />
        </g>
      )}
      {label === 'Checklist' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="2.4" width="10" height="11.2" rx="1" />
          <path d="M5 6.2 6 7.2 7.8 5.2M5 10.6 6 11.6 7.8 9.6M9.2 6.4h2.2M9.2 10.8h2.2" />
        </g>
      )}
      {label === 'Package' && (
        <g
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
          strokeDasharray="2 2"
        >
          <path d="M2.5 13V5.5h4.2l1.3 1.5H13.5V13z" />
        </g>
      )}
      {label === 'Practice' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M8 2.5 13.2 5.5v5L8 13.5 2.8 10.5v-5z" />
        </g>
      )}
      {label === 'Epic' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M4 2.5v11" />
          <path d="M4 3.5h8L10.5 6 12 8.5H4" />
        </g>
      )}
      {label === 'Sub-epic' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M5.5 4v9" />
          <path d="M5.5 4.5h6.5L10.5 6.5 12 8.5H5.5" />
        </g>
      )}
      {label === 'Story' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <rect x="3" y="2.5" width="10" height="11" rx="1" />
          <path d="M5.5 6h5M5.5 8.5h5M5.5 11h3" />
        </g>
      )}
      {label === 'Background' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <rect x="5" y="2.5" width="8" height="8" />
          <path d="M3 5.5h8V13.5H3z" />
        </g>
      )}
      {label === 'Scenario' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
          <circle cx="4" cy="12" r="1.6" />
          <circle cx="12" cy="4" r="1.6" />
          <path d="M5.3 10.8 10.7 5.2" />
        </g>
      )}
      {label === 'Step' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round">
          <path d="M3 12.5h3.5V9h3.5V5.5H13" />
        </g>
      )}
      {label === 'Example' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6.2 3.2C4.8 3.2 4 4.2 4 5.4v1.4L2.6 8 4 9.2v1.4c0 1.2.8 2.2 2.2 2.2" />
          <path d="M9.8 3.2c1.4 0 2.2 1 2.2 2.2v1.4L13.4 8 12 9.2v1.4c0 1.2-.8 2.2-2.2 2.2" />
        </g>
      )}
      {label === 'Bounded context' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeDasharray="2 1.4">
          <rect x="2.5" y="3" width="11" height="10" rx="2" />
        </g>
      )}
      {label === 'Aggregate' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2.5" y="2.5" width="5" height="5" />
          <rect x="8.5" y="2.5" width="5" height="5" />
          <rect x="5.5" y="8.5" width="5" height="5" />
        </g>
      )}
      {label === 'Entity' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="10" height="10" rx="0.5" />
          <circle cx="8" cy="8" r="1.3" fill="currentColor" stroke="none" />
        </g>
      )}
      {label === 'Entity root' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3" y="3" width="10" height="10" rx="0.5" />
          <path d="M3 6.5h10" />
          <rect x="3.4" y="3.4" width="9.2" height="2.8" fill="currentColor" stroke="none" />
        </g>
      )}
      {label === 'Value object' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="3.5" y="3.5" width="9" height="9" rx="2" />
        </g>
      )}
      {label === 'Repository' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M3 5.5c0-1.2 2.2-2 5-2s5 .8 5 2v5c0 1.2-2.2 2-5 2s-5-.8-5-2z" />
          <path d="M3 5.5c0 1.2 2.2 2 5 2s5-.8 5-2" />
        </g>
      )}
      {label === 'Domain event' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M8 2.5 13 13H3z" />
        </g>
      )}
      {label === 'Domain service' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="8" cy="8" r="4.5" />
          <circle cx="8" cy="8" r="1.4" fill="currentColor" stroke="none" />
        </g>
      )}
      {label === 'Specification' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M4 2.5h6l2 2V13.5H4z" />
          <path d="M6 8h4M6 10.5h3" />
        </g>
      )}
      {label === 'Description' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
          <path d="M3 3.5h10v6.5H8.2L6 12.5V10H3z" />
        </g>
      )}
      {label === 'Context' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="2.5" y="2.5" width="11" height="11" rx="2" />
          <rect x="5.2" y="5.2" width="5.6" height="5.6" rx="1" />
        </g>
      )}
      {label === 'Observation' && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="8" cy="8" r="5" />
          <path d="M5.4 8.2 7.2 10l3.4-4" />
        </g>
      )}
      {!KNOWN_MARKS.has(label) && (
        <g fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="8" cy="8" r="4.5" />
        </g>
      )}
    </svg>
  );
}

