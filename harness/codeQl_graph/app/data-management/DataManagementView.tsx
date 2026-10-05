type DataManagementViewProps = {
  loading: boolean;
  folder: string;
  status: string;
  onCreate: () => void;
  onMerge: () => void;
  onReload: () => void;
};

export function DataManagementView({ loading, folder, status, onCreate, onMerge, onReload }: DataManagementViewProps) {
  return (
    <div className="database-actions" aria-busy={loading}>
      <button type="button" className="btn-refresh" data-testid="create-database" disabled={loading || !folder} onClick={onCreate}>
        Create database
      </button>
      <button type="button" className="btn-refresh" data-testid="refresh-master" disabled={loading || !folder} onClick={onMerge}>
        Merge working to master
      </button>
      <button type="button" className="btn-refresh" data-testid="reload-working-copy" disabled={loading || !folder} onClick={onReload}>
        Reload working copy
      </button>
      {status ? (
        <p className="work-progress is-done" data-testid="work-progress" aria-live="polite">
          {status}
        </p>
      ) : null}
    </div>
  );
}
