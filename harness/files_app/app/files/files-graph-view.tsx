import { useSyncExternalStore, type MouseEvent } from 'react'

import type { ExplorerEntryData } from '@cdd/space/session/session'

import type { FilesPage } from './files-page'

function useFilesState(page: FilesPage) {
  return useSyncExternalStore(page.store.subscribe, () => page.store.state)
}

// A press with Ctrl, Cmd or Shift selects a node beside those already selected, as a file manager selects several.
const isAlso = (event: MouseEvent): boolean => event.ctrlKey || event.metaKey || event.shiftKey

// One node of a practice tree: a toggle while it holds entries below it, its name, which selects it, and its type.
function GraphEntryView({ page, entry }: { page: FilesPage; entry: ExplorerEntryData }) {
  useFilesState(page)
  const below = page.graph.childrenOf(entry)
  const hasBelow = below.length > 0 || entry.children_left_out > 0
  const isOpen = page.graph.isOpen(entry)
  return (
    <li className="graph-entry">
      <span className={`graph-row ${page.graph.isSelected(entry) ? 'is-selected' : ''}`}>
        {hasBelow ? (
          <button className="graph-toggle" aria-expanded={isOpen} aria-label={`${isOpen ? 'Close' : 'Open'} ${entry.name}`} onClick={() => void page.graph.toggle(entry)}>
            {isOpen ? '▾' : '▸'}
          </button>
        ) : (
          <span className="graph-toggle" />
        )}
        <button className="graph-node" aria-pressed={page.graph.isSelected(entry)} title={`${entry.type} ${entry.name}`} onClick={event => void page.graph.select(entry, isAlso(event))}>
          {entry.name}
        </button>
        <span className="graph-type">{entry.type}</span>
      </span>
      {isOpen && below.length ? (
        <ul className="graph-tree">
          {below.map(child => (
            <GraphEntryView key={child.node_id} page={page} entry={child} />
          ))}
        </ul>
      ) : null}
    </li>
  )
}

// The file bar's graph view: the practice trees of the session's graph holding only the nodes of the files the bar
// lists, each collapsed until a person opens it.
export function FilesGraphView({ page }: { page: FilesPage }) {
  const { graph } = useFilesState(page)
  if (graph.problem) return <p className="files-note">{graph.problem}</p>
  if (graph.isReading && !graph.trees) return <p className="files-note">Reading the session's graph…</p>
  if (!graph.trees?.length) return <p className="files-note">The graph holds no node of these files.</p>
  return (
    <ul className="graph-tree" aria-label="Graph">
      {graph.trees.map(tree => (
        <GraphEntryView key={tree.node_id} page={page} entry={tree} />
      ))}
    </ul>
  )
}
