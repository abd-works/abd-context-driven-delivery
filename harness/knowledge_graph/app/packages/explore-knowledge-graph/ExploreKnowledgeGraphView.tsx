import { useEffect, useState } from 'react';
import { useKnowledgeGraph } from './knowledge-graph/knowledge-graph-client';
import {
  pickerRelativePath,
  scanSourceFiles,
  type WorkspaceFile,
} from './knowledge-graph/workspace';
import wordmarkBlack from './brand/abd.works.wordmark.black.svg?url';
import wordmarkWhite from './brand/abd.works.wordmark.white.svg?url';

/**
 * ExploreKnowledgeGraphView — feature view.
 * Sources: harness/knowledge_graph/.context/knowledge-graph-explorer-sketch.md
 */
export function ExploreKnowledgeGraphView({ graphId = '' }: { graphId?: string }) {
  const {
    loading,
    folder: scannedFolder,
    listedNodes,
    selectedNode,
    sourceFile,
    selectNode,
    followRelationship,
    filterGraph,
    selectFolder,
  } = useKnowledgeGraph(graphId);
  const [rule, setRule] = useState('');
  const [violations, setViolations] = useState(false);
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
    const picked: WorkspaceFile[] = [];
    let folderName = 'workspace';
    for (const file of Array.from(list)) {
      const mapped = pickerRelativePath(file.webkitRelativePath || file.name);
      folderName = mapped.folder;
      picked.push({
        relativePath: mapped.relativePath,
        text: await file.text(),
      });
    }
    const files = scanSourceFiles(picked);
    setFolder(folderName);
    selectFolder({ folder: folderName, files });
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
        </header>
        <div className="toolbar">
          <div className="folder-scan">
            <span className="btn-primary">
              Choose folder
              <input
                data-testid="working-folder"
                type="file"
                multiple
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
            {folder ? (
              <span className="chosen-folder" data-testid="chosen-folder">
                {folder}
              </span>
            ) : null}
          </div>
          <div className="filters">
            <label>
              violations
              <input
                type="checkbox"
                checked={violations}
                onChange={(event) => {
                  const next = event.target.checked;
                  setViolations(next);
                  filterGraph({ violations: next, rule: rule || undefined });
                }}
              />
            </label>
            <label>
              rule
              <input
                type="text"
                value={rule}
                onChange={(event) => setRule(event.target.value)}
                onBlur={() =>
                  filterGraph({ violations, rule: rule || undefined })
                }
              />
            </label>
          </div>
        </div>
        <div className="split">
          <nav className="panel tree" data-testid="practice-graph-tree">
            {loading && <p className="empty-state">Loading KnowledgeGraph...</p>}
            {!loading && listedNodes.length === 0 && (
              <p className="empty-state">
                Choose a folder to scan the working area.
              </p>
            )}
            <ul className="tree">
              {listedNodes.map((node) => (
                <li key={node.node_id}>
                  <button
                    type="button"
                    className={
                      selectedNode?.node_id === node.node_id ? 'selected' : ''
                    }
                    onClick={() => selectNode(node.node_id)}
                  >
                    {node.name}
                  </button>
                  <ul>
                    {Object.entries(node.rule_statuses).map(([slug, status]) => (
                      <li key={slug} className={`rule-status ${status}`}>
                        {slug} {status}
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
          </nav>
          <section className="panel" data-testid="source-file">
            {sourceFile ? (
              <pre className="source-file">
                <h2>{sourceFile.file}</h2>
                <code data-start-line={sourceFile.start_line}>
                  {sourceFile.text}
                </code>
              </pre>
            ) : (
              <p className="empty-state">No source file</p>
            )}
          </section>
        </div>
        {selectedNode && !selectedNode.is_file && (
          <button
            type="button"
            hidden
            onClick={() =>
              selectedNode && followRelationship(selectedNode.node_id)
            }
          >
            follow
          </button>
        )}
      </div>
    </main>
  );
}
