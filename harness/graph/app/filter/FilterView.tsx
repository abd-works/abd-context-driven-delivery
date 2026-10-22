import type { FilterSelection } from './FilterClient';
import { overlayCatalogLabel, overlayPathLabel } from '../overlay-labels';

type FilterViewProps = {
  open: boolean;
  selection: FilterSelection;
  practices: string[];
  nodeTypes: string[];
  relationships: string[];
  rules: string[];
  availableOverlays?: string[];
  overlayApplying?: boolean;
  overlayHint?: string;
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
  overlayHint = '',
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
        {availableOverlays.length > 0 ? (
          <div className="overlay-catalog" data-testid="overlay-catalog">
            {availableOverlays
              .filter((name) => !selection.overlays.some((item) => overlayLabel(item) === name))
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
        ) : null}
        {overlayApplying ? <p className="overlay-status" data-testid="overlay-applying">Applying overlay…</p> : null}
        {overlayHint ? <p className="overlay-hint" data-testid="overlay-hint">{overlayHint}</p> : null}
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
      </div>
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
        options={[...rules].sort((left, right) => left.localeCompare(right))}
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
    </div>
  );
}

function overlayId(path: string): string {
  const trimmed = path.replace(/[/\\]+$/, '');
  const parts = trimmed.split(/[/\\]/);
  return parts[parts.length - 1] || path;
}

function overlayLabel(path: string): string {
  return overlayCatalogLabel(overlayId(path));
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
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}) {
  return (
    <div className="filter-list">
      <div className="filter-heading">
        <span className="filter-label">{label}</span>
        <div className="filter-actions">
          <button type="button" onClick={() => onChange(options)}>
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
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}

