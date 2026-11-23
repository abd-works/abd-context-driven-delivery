import type { FilterSelection } from './filter-selection';
import { overlayCatalogLabel, overlayId, overlayPathLabel } from '../labels/overlay-labels';

type FilterViewProps = {
  open: boolean;
  selection: FilterSelection;
  practices: string[];
  nodeTypes: string[];
  relationships: string[];
  rules: string[];
  availableOverlays?: string[];
  overlayApplying?: boolean;
  onChange: (selection: FilterSelection) => void;
  onAddOverlay: () => void;
  onAddNamedOverlay?: (name: string) => void;
  onRemoveOverlay: (overlay: string) => void;
};

export function FilterView({
  open,
  selection,
  practices,
  nodeTypes,
  relationships,
  rules,
  availableOverlays = [],
  overlayApplying = false,
  onChange,
  onAddOverlay,
  onAddNamedOverlay,
  onRemoveOverlay,
}: FilterViewProps) {
  return (
    <div className="filters" hidden={!open}>
      <FilterSelect
        label="Practice"
        testId="filter-practice"
        options={practices}
        selected={selection.practices}
        onChange={(practices) => onChange({ ...selection, practices })}
      />
      <div className="filter-list overlay-list">
        <div className="filter-heading">
          <span className="filter-label">Pattern overlay</span>
          <div className="filter-actions">
            <button type="button" data-testid="overlay-add" onClick={onAddOverlay}>
              Add folder…
            </button>
          </div>
        </div>
        <OverlayCatalog selection={selection} availableOverlays={availableOverlays} overlayApplying={overlayApplying} onAddNamedOverlay={onAddNamedOverlay} />
        {overlayApplying ? <p className="overlay-status" data-testid="overlay-applying">Applying overlay…</p> : null}
        <OverlayItems selection={selection} onRemoveOverlay={onRemoveOverlay} />
      </div>
      <NodeFilterLists selection={selection} nodeTypes={nodeTypes} relationships={relationships} rules={rules} onChange={onChange} />
    </div>
  );
}

// The named overlays the server offers that the filter does not use yet, each a button that adds it.
function OverlayCatalog({
  selection,
  availableOverlays,
  overlayApplying,
  onAddNamedOverlay,
}: {
  selection: FilterSelection;
  availableOverlays: string[];
  overlayApplying: boolean;
  onAddNamedOverlay?: (name: string) => void;
}) {
  if (availableOverlays.length === 0) return null;
  return (
    <div className="overlay-catalog" data-testid="overlay-catalog">
      {availableOverlays
        .filter((name) => !selection.overlays.some((item) => overlayId(item) === name))
        .map((name) => (
          <button
            key={name}
            type="button"
            className="overlay-catalog-item"
            data-testid={`overlay-add-${name}`}
            disabled={overlayApplying}
            onClick={() => onAddNamedOverlay?.(name)}
          >
            {overlayCatalogLabel(name)}
          </button>
        ))}
    </div>
  );
}

// The overlays the filter uses, each with a button that removes it; a hint on adding one while it uses none.
function OverlayItems({ selection, onRemoveOverlay }: { selection: FilterSelection; onRemoveOverlay: (overlay: string) => void }) {
  return (
    <ul className="overlay-items" data-testid="overlay-list">
      {selection.overlays.length === 0 ? (
        <li className="overlay-empty">
          No active overlay. Click <strong>Lern domain driven</strong> above (or Add folder…), then wait for the graph
          to rebuild.
        </li>
      ) : (
        selection.overlays.map((overlay) => (
          <li key={overlay} className="overlay-item">
            <span className="overlay-path" title={overlay}>{overlayPathLabel(overlay)}</span>
            <button
              type="button"
              className="overlay-remove"
              data-testid={`overlay-remove-${overlayId(overlay)}`}
              aria-label={`Remove overlay ${overlayPathLabel(overlay)}`}
              onClick={() => onRemoveOverlay(overlay)}
            >
              ×
            </button>
          </li>
        ))
      )}
    </ul>
  );
}

type NodeFilterListsProps = {
  selection: FilterSelection;
  nodeTypes?: string[];
  relationships?: string[];
  rules?: string[];
  onChange: (selection: FilterSelection) => void;
};

// The node filter's lists, as every page that filters a graph's nodes shows them: node types, connectors, rules, and the
// Violations switch.
export function NodeFilterLists({ selection, nodeTypes, relationships, rules, onChange }: NodeFilterListsProps) {
  return (
    <>
      <FilterSelect
        label="Node"
        testId="filter-node"
        options={nodeTypes}
        selected={selection.node_types}
        onChange={(node_types) => onChange({ ...selection, node_types })}
      />
      <FilterSelect
        label="Connector"
        testId="filter-connector"
        options={relationships}
        selected={selection.relationships}
        onChange={(relationships) => onChange({ ...selection, relationships })}
      />
      <FilterSelect
        label="Rule"
        testId="filter-rule"
        options={[...(rules ?? [])].sort((left, right) => left.localeCompare(right))}
        selected={selection.rules}
        onChange={(rules) => onChange({ ...selection, rules })}
      />
      <div className="filter-extras">
        <button
          type="button"
          className={selection.violations ? 'filter-switch is-on' : 'filter-switch'}
          aria-pressed={selection.violations}
          onClick={() => onChange({ ...selection, violations: !selection.violations })}
        >
          <span className="filter-switch-label">Violations</span>
          <span className="filter-switch-track" aria-hidden="true">
            <span className="filter-switch-knob" />
          </span>
        </button>
      </div>
    </>
  );
}

function FilterSelect({
  label,
  testId,
  options,
  selected,
  onChange,
}: {
  label: string;
  testId: string;
  options?: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}) {
  return (
    <div className="filter-list">
      <div className="filter-heading">
        <span className="filter-label">{label}</span>
        <div className="filter-actions">
          <button type="button" onClick={() => onChange(options ?? [])}>
            All
          </button>
          <button type="button" onClick={() => onChange([])}>
            None
          </button>
        </div>
      </div>
      <select
        multiple
        data-testid={testId}
        value={selected}
        onChange={(event) => {
          onChange(Array.from(event.target.selectedOptions).map((option) => option.value));
        }}
      >
        {(options ?? []).map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}

