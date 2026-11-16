import type { KeyboardEvent } from 'react';

type FolderBarProps = {
  folder: string;
  loadedFolder: string;
  filtersOpen: boolean;
  onFolder: (folder: string) => void;
  onLoad: (folder: string) => void;
  onBrowse: () => void;
  onToggleFilters: () => void;
};

// The folder the graph is read from: a person types it or browses to it, and it loads on Enter or when they leave it.
export function FolderBar({ folder, loadedFolder, filtersOpen, onFolder, onLoad, onBrowse, onToggleFilters }: FolderBarProps) {
  const loadOnEnter = (event: KeyboardEvent<HTMLInputElement>) => event.key === 'Enter' && onLoad(folder);
  const loadWhenChanged = () => folder.trim() && folder.trim() !== loadedFolder && onLoad(folder.trim());
  return (
    <div className="folder-scan">
      <button
        type="button"
        className="btn-primary"
        data-testid="working-folder"
        title="Select the session path, the folder the session works in, to load the Knowledge Graph"
        onClick={onBrowse}
      >
        Session path
      </button>
      <button
        type="button"
        className="filter-toggle"
        data-testid="toggle-filters"
        aria-expanded={filtersOpen}
        aria-label={filtersOpen ? 'Collapse filters' : 'Expand filters'}
        onClick={onToggleFilters}
      >
        {filtersOpen ? '▼' : '▶'}
      </button>
      <input
        className="chosen-folder"
        data-testid="chosen-folder"
        value={folder}
        placeholder="Session path"
        spellCheck={false}
        onChange={(event) => onFolder(event.target.value)}
        onKeyDown={loadOnEnter}
        onBlur={loadWhenChanged}
      />
    </div>
  );
}
