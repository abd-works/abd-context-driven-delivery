import { useSyncExternalStore, type MouseEvent } from 'react'

import type { ExplorerEntryData } from '@cdd/space/session/session'
import { LoadProgressView } from '@graph-app/graph/LoadProgressView'
import { KindMark, kindLabel } from '@graph-app/labels/kind-mark'

import type { FilesPage } from './files-page'

function useFilesState(page: FilesPage) {
  return useSyncExternalStore(page.store.subscribe, () => page.store.state)
}

// A press with Ctrl, Cmd or Shift selects a node beside those already selected, as a file manager selects several.
const isAlso = (event: MouseEvent): boolean => event.ctrlKey || event.metaKey || event.shiftKey

// A node's row as the Graph app draws it: a twist while it holds entries below it, then its kind's mark and its name,
// which select it.
function GraphRowView({ page, entry, hasBelow }: { page: FilesPage; entry: ExplorerEntryData; hasBelow: boolean }) {
  const isOpen = page.graph.isOpen(entry)
  const isSelected = page.graph.isSelected(entry)
  return (
    <div className="tree-row">
      {hasBelow ? (
        <button className="tree-twist" aria-expanded={isOpen} aria-label={`${isOpen ? 'Close' : 'Open'} ${entry.name}`} onClick={() => void page.graph.toggle(entry)}>
          {isOpen ? '▼' : '▶'}
        </button>
      ) : (
        <span className="tree-twist-spacer" />
      )}
      <button className={`graph-node ${isSelected ? 'selected' : ''}`} aria-pressed={isSelected} title={`${kindLabel(entry.type, false)} ${entry.name}`} onClick={event => void page.graph.select(entry, isAlso(event))}>
        <KindMark kind={entry.type} isFile={false} />
        <span className="node-name">{entry.name}</span>
      </button>
    </div>
  )
}

// One node of a practice tree, with the entries below it while it is open.
function GraphEntryView({ page, entry }: { page: FilesPage; entry: ExplorerEntryData }) {
  useFilesState(page)
  const below = page.graph.childrenOf(entry)
  const isOpen = page.graph.isOpen(entry)
  return (
    <li className="graph-entry" data-kind={entry.type}>
      <GraphRowView page={page} entry={entry} hasBelow={below.length > 0 || entry.children_left_out > 0} />
      {isOpen && below.length ? (
        <ul>
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
  if (graph.isReading) return <LoadProgressView loadingLabel="Reading the session's graph…" loadingLog={graph.log} />
  if (!Array.isArray(graph.trees) || !graph.trees.length) return <p className="files-note">The graph holds no node of these files.</p>
  return (
    <ul className="tree graph-tree" aria-label="Graph">
      {graph.trees.map(tree => (
        <GraphEntryView key={tree.node_id} page={page} entry={tree} />
      ))}
    </ul>
  )
}
