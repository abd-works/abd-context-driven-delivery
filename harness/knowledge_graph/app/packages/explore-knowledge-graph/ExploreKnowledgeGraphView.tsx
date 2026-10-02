import { type ChangeEvent, useEffect, useState } from 'react';
import { useKnowledgeGraph } from './use-knowledge-graph';
import {
  isScanSourcePath,
  pickerRelativePath,
  PICKER_UPLOAD_LIMIT,
  scanSourceFiles,
  type WorkspaceFile,
} from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/workspace';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';

/**
 * ExploreKnowledgeGraphView — feature view.
 * Sources: harness/knowledge_graph/.context/knowledge-graph-explorer-sketch.md
 */
export function ExploreKnowledgeGraphView({ graphId = '' }: { graphId?: string }) {
  const [filtersOpen, setFiltersOpen] = useState(true);
  const {
    loading,
    workStatus,
    folder: scannedFolder,
    html,
    selectNode,
    selectFolder,
    refreshGraph,
    createDatabase,
    refreshMaster,
    reloadWorkingCopy,
    scanError,
  } = useKnowledgeGraph(graphId);
  const [folder, setFolder] = useState(scannedFolder);
  const [theme, setTheme] = useState(
    () => document.documentElement.dataset.theme ?? '',
  );

  useEffect(() => {
    if (scannedFolder) {
      setFolder(scannedFolder);
    }
  }, [scannedFolder]);

  function applyTheme(next: '' | 'engineering') {
    setTheme(next);
    if (next) {
      document.documentElement.dataset.theme = next;
    } else {
      delete document.documentElement.dataset.theme;
    }
    window.localStorage.setItem('kg-theme', next);
  }

  async function pickFolder(list: FileList | null) {
    if (!list || list.length === 0) {
      return;
    }
    let folderName = 'workspace';
    const source: File[] = [];
    for (const file of Array.from(list)) {
      const mapped = pickerRelativePath(file.webkitRelativePath || file.name);
      folderName = mapped.folder;
      if (isScanSourcePath(mapped.relativePath)) {
        source.push(file);
      }
    }
    setFolder(folderName);
    if (source.length === 0 || source.length > PICKER_UPLOAD_LIMIT) {
      selectFolder({ folder: folderName });
      return;
    }
    const picked: WorkspaceFile[] = [];
    for (const file of source) {
      const mapped = pickerRelativePath(file.webkitRelativePath || file.name);
      picked.push({
        relativePath: mapped.relativePath,
        text: await file.text(),
      });
    }
    selectFolder({ folder: folderName, files: scanSourceFiles(picked) });
  }

  const engineering = theme === 'engineering';

  return (
    <main className="explore-knowledge-graph">
      <div className="knowledge-graph-explorer">
        <header className="site-nav">
          <div className="nav-brand">
            <a className="nav-logo" href="/" aria-label="abd.works">
              <img
                src={engineering ? wordmarkWhite : wordmarkBlack}
                alt="abd.works"
              />
            </a>
            <p className="page-hero-label">Knowledge graph</p>
          </div>
          <div className="nav-actions">
            <div className="mode-toggle" role="group" aria-label="Theme">
              <button
                type="button"
                className={engineering ? '' : 'is-active'}
                onClick={() => applyTheme('')}
              >
                <span className="mode-label">Executive</span>
                <span className="mode-icon" aria-hidden="true">
                  ☀
                </span>
              </button>
              <button
                type="button"
                className={engineering ? 'is-active' : ''}
                onClick={() => applyTheme('engineering')}
              >
                <span className="mode-label">Engineering</span>
                <span className="mode-icon" aria-hidden="true">
                  ☾
                </span>
              </button>
            </div>
            <div className="database-actions" aria-busy={loading}>
              <button
                type="button"
                className="btn-refresh"
                data-testid="create-database"
                disabled={loading || !folder}
                onClick={() => createDatabase(folder)}
              >
                Create database
              </button>
              <button
                type="button"
                className="btn-refresh"
                data-testid="refresh-master"
                disabled={loading || !folder}
                onClick={() => refreshMaster(folder)}
              >
                Refresh master
              </button>
              <button
                type="button"
                className="btn-refresh"
                data-testid="reload-working-copy"
                disabled={loading || !folder}
                onClick={() => reloadWorkingCopy(folder)}
              >
                Reload working copy
              </button>
            </div>
            <button
              type="button"
              className="btn-refresh"
              data-testid="refresh-graph"
              disabled={loading}
              onClick={() => refreshGraph()}
            >
              Refresh
            </button>
            {workStatus ? (
              <p
                className={`work-progress is-${workStatus.phase}`}
                data-testid="work-progress"
                aria-live="polite"
              >
                {workStatus.phase === 'working'
                  ? `${workStatus.action}… ${workStatus.seconds}s`
                  : workStatus.phase === 'done'
                    ? `${workStatus.action} done`
                    : workStatus.detail || `${workStatus.action} failed`}
              </p>
            ) : null}
          </div>
        </header>
        <div className="toolbar">
          <div className="folder-scan">
            <span className="btn-primary">
              Repo folder
              <input
                data-testid="working-folder"
                type="file"
                multiple
                title="Select a repo folder to load the Knowledge Graph"
                onChange={(event) => {
                  void pickFolder(event.target.files);
                  event.target.value = '';
                }}
                {...({
                  webkitdirectory: '',
                  directory: '',
                } as Record<string, string>)}
              />
            </span>
            <button
              type="button"
              className="filter-toggle"
              data-testid="toggle-filters"
              aria-expanded={filtersOpen}
              aria-label={filtersOpen ? 'Collapse filters' : 'Expand filters'}
              onClick={() => setFiltersOpen((open) => !open)}
            >
              {filtersOpen ? '▼' : '▶'}
            </button>
            {folder ? (
              <input
                className="chosen-folder"
                data-testid="chosen-folder"
                value={folder}
                spellCheck={false}
                onChange={(event: ChangeEvent<HTMLInputElement>) => {
                  setFolder(event.target.value);
                }}
                onBlur={() => {
                  const next = folder.trim();
                  if (next && next !== scannedFolder) {
                    selectFolder({ folder: next });
                  }
                }}
                onKeyDown={(event) => {
                  if (event.key !== 'Enter') {
                    return;
                  }
                  const next = folder.trim();
                  if (next) {
                    selectFolder({ folder: next });
                  }
                }}
              />
            ) : null}
          </div>
          <div className="filters" hidden={!filtersOpen} />
        </div>
        <div
          className="split"
          data-testid="practice-graph-tree"
          onClick={(event) => {
            const target = (event.target as HTMLElement).closest('[data-node-id]');
            if (target) {
              selectNode(target.getAttribute('data-node-id') ?? '');
            }
          }}
        >
          {loading && (
            <p className="empty-state" data-testid="graph-loading">
              {workStatus
                ? `${workStatus.action}… ${workStatus.seconds}s`
                : 'Loading KnowledgeGraph...'}
            </p>
          )}
          {!loading && scanError && (
            <p className="empty-state" data-testid="scan-error">
              {scanError}
            </p>
          )}
          <div
            data-testid="source-file"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        </div>
      </div>
    </main>
  );
}
