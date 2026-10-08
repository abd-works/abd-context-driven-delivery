type Comparison = {
  older: boolean;
  practice: string;
  dates: Record<string, string>;
};

export type Staleness = {
  master_stale: {
    older_than_worktree: Comparison;
    older_than_code: Comparison;
  };
  worktree_stale: {
    older_than_code: Comparison;
    older_than_master: Comparison;
  };
  graph_cache_stale: {
    older_than_worktree: Comparison;
    older_than_master: Comparison;
    older_than_code: Comparison;
  };
  dates: {
    graph_cache: string;
    practices: { practice: string; master: string; worktree: string; code: string }[];
  };
};

type DataManagementViewProps = {
  loading: boolean;
  folder: string;
  status: string;
  staleness: Staleness | null;
  onCreate: () => void;
  onMerge: () => void;
  onReload: () => void;
  onSerialize: () => void;
};

export function DataManagementView({
  loading,
  folder,
  status,
  staleness,
  onCreate,
  onMerge,
  onReload,
  onSerialize,
}: DataManagementViewProps) {
  const disabled = loading || !folder;
  const masterBehindCode = Boolean(staleness?.master_stale?.older_than_code?.older);
  const masterBehindWorktree = Boolean(staleness?.master_stale?.older_than_worktree?.older);
  const worktreeBehind =
    Boolean(staleness?.worktree_stale?.older_than_code?.older) || Boolean(staleness?.worktree_stale?.older_than_master?.older);
  const cacheBehind =
    Boolean(staleness?.graph_cache_stale?.older_than_worktree?.older) ||
    Boolean(staleness?.graph_cache_stale?.older_than_master?.older) ||
    Boolean(staleness?.graph_cache_stale?.older_than_code?.older);
  return (
    <div className="database-actions" aria-busy={loading}>
      <Command
        testId="create-database"
        label="Create database"
        stale={masterBehindCode}
        disabled={disabled}
        onClick={onCreate}
        detail={staleness ? describe('Master older than code', staleness.master_stale.older_than_code) : ''}
      />
      <Command
        testId="refresh-master"
        label="Merge working to master"
        stale={masterBehindWorktree}
        disabled={disabled}
        onClick={onMerge}
        detail={staleness ? describe('Master older than working copy', staleness.master_stale.older_than_worktree) : ''}
      />
      <Command
        testId="reload-working-copy"
        label="Reload working copy"
        stale={worktreeBehind}
        disabled={disabled}
        onClick={onReload}
        detail={
          staleness
            ? [
                describe('Working copy older than code', staleness.worktree_stale.older_than_code),
                describe('Working copy older than master', staleness.worktree_stale.older_than_master),
              ].join('\n')
            : ''
        }
      />
      <Command
        testId="serialize-graph-cache"
        label="Serialize graph cache"
        stale={cacheBehind}
        disabled={disabled}
        onClick={onSerialize}
        detail={
          staleness
            ? [
                describe('Graph cache older than working copy', staleness.graph_cache_stale.older_than_worktree),
                describe('Graph cache older than master', staleness.graph_cache_stale.older_than_master),
                describe('Graph cache older than code', staleness.graph_cache_stale.older_than_code),
              ].join('\n')
            : ''
        }
      />
      {status ? (
        <p className="work-progress is-done" data-testid="work-progress" aria-live="polite">
          {status}
        </p>
      ) : null}
    </div>
  );
}

function Command({
  testId,
  label,
  stale,
  disabled,
  onClick,
  detail,
}: {
  testId: string;
  label: string;
  stale: boolean;
  disabled: boolean;
  onClick: () => void;
  detail: string;
}) {
  return (
    <span className="command">
      <button
        type="button"
        className={stale ? 'btn-refresh is-stale' : 'btn-refresh'}
        data-testid={testId}
        data-stale={stale ? 'true' : 'false'}
        disabled={disabled}
        onClick={onClick}
      >
        {label}
      </button>
      {detail ? (
        <span className="staleness-tip" role="tooltip" data-testid={`${testId}-staleness`}>
          {detail}
        </span>
      ) : null}
    </span>
  );
}

function describe(label: string, comparison: Comparison): string {
  const practice = comparison.practice ? ` (${comparison.practice})` : '';
  const state = comparison.older ? 'older' : 'current';
  const dates = Object.entries(comparison.dates)
    .map(([name, value]) => `${name} ${value || 'missing'}`)
    .join('\n');
  return `${label}: ${state}${practice}\n${dates}`;
}
