import type { FilterSelection } from './FilterClient';

type FilterViewProps = {
  open: boolean;
  selection: FilterSelection;
  practices: string[];
  nodeTypes: string[];
  relationships: string[];
  rules: string[];
  onChange: (selection: FilterSelection) => void;
};

export function FilterView({
  open,
  selection,
  practices,
  nodeTypes,
  relationships,
  rules,
  onChange,
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
        options={rules}
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
