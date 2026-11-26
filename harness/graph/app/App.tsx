import { useState } from 'react';
import { useExplorerFilter, type ExplorerFilter } from './explorer/explorer-filter';
import { useGraphLoad, type GraphLoad } from './explorer/graph-load';
import { useLoadStatus, useServerProgress, type LoadStatus } from './explorer/load-status';
import { useOverlays, type Overlays } from './explorer/overlays';
import { usePageFolder, type PageFolder } from './explorer/page-folder';
import { useSourcePane, type SourcePane } from './explorer/source-pane';
import { FilterView } from './filter/FilterView';
import { FolderBar } from './graph/FolderBar';
import { GraphView } from './graph/GraphView';
import { SiteNav } from './SiteNav';
import { SourceView } from './source/SourceView';
import { failures } from './graph/graph-page';

// The Graph app's page: the folder its graph is read from, the filter, the tree, and the chosen node's source. Every
// failure goes through failures.fail: shown on the page and sent once to the chat that opened it (?chat=).
export function App() {
  const status = useLoadStatus();
  useServerProgress(status);
  const folder = usePageFolder();
  const filter = useExplorerFilter(folder, status);
  const overlays = useOverlays(filter, folder, status);
  const graph = useGraphLoad(filter, overlays, status);
  const pane = useSourcePane();
  return (
    <main className="explore-knowledge-graph">
      <div className="knowledge-graph-explorer">
        <SiteNav canReload={!status.loading && folder.chosen} onReload={() => void graph.load(folder.value, true)} />
        <ExplorerToolbar folder={folder} filter={filter} overlays={overlays} graph={graph} />
        <ExplorerSplit status={status} filter={filter} pane={pane} />
      </div>
    </main>
  );
}

// The bar above the tree: the folder the graph is read from, and the filter, which the person can fold away.
function ExplorerToolbar({ folder, filter, overlays, graph }: { folder: PageFolder; filter: ExplorerFilter; overlays: Overlays; graph: GraphLoad }) {
  const [filtersOpen, setFiltersOpen] = useState(true);
  return (
    <div className="toolbar">
      <FolderBar
        folder={folder.value}
        loadedFolder={graph.loadedFolder}
        filtersOpen={filtersOpen}
        onFolder={(next) => folder.choose(next)}
        onLoad={(root) => void graph.load(root)}
        onBrowse={() => void graph.browse()}
        onToggleFilters={() => setFiltersOpen((open) => !open)}
      />
      <FilterView
        open={filtersOpen}
        selection={filter.selection}
        practices={graph.practices}
        nodeTypes={filter.offered.offered_node_types}
        relationships={filter.offered.relationships}
        rules={filter.offered.rules}
        onChange={(next) => void filter.apply(next)}
        availableOverlays={overlays.available}
        overlayApplying={overlays.applying}
        onAddOverlay={() => void overlays.addFolder()}
        onAddNamedOverlay={(name) => overlays.addNamed(name)}
        onRemoveOverlay={(overlay) => overlays.remove(overlay)}
      />
    </div>
  );
}

// The tree of the graph beside the source of the node chosen in it.
function ExplorerSplit({ status, filter, pane }: { status: LoadStatus; filter: ExplorerFilter; pane: SourcePane }) {
  return (
    <div className="split">
      <GraphView
        trees={filter.trees}
        loading={status.loading}
        loadingLabel={status.label}
        loadingLog={status.log}
        error={status.error}
        selectedId={pane.selectedId}
        activeRule={pane.activeRule}
        onSelect={(selection) => void pane.choose(selection)}
        onOpenBranch={(nodeId) => filter.openBranch(nodeId)}
      />
      <SourceView
        source={pane.source}
        note={pane.note}
        violation={pane.violation}
        rules={pane.rulesIn(filter.trees)}
        activeRule={pane.activeRule}
        onSelectRule={(name) => pane.chooseRule(filter.trees, name)}
        fixes={{ one: failures.fixOne }}
      />
    </div>
  );
}
