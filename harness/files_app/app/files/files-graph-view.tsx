import { useState, useSyncExternalStore, type MouseEvent } from 'react'

import type { GraphRuleData } from '@cdd/harness/graph/graph'
import type { ExplorerEntryData } from '@cdd/space/session/session'
import { NodeFilterLists } from '@graph-app/filter/FilterView'
import { LoadProgressView } from '@graph-app/graph/LoadProgressView'
import { KindMark, kindLabel } from '@graph-app/labels/kind-mark'
import { FixButton } from '@source-view/FixButton'

import { isFailing, ruleTitleOf } from './files-graph'
import type { FilesPage } from './files-page'
import type { FilesGraphState } from './files-state'

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
      <button className={['graph-node', isSelected ? 'selected' : '', page.graph.breaksARule(entry) ? 'tree-violating' : ''].filter(Boolean).join(' ')} aria-pressed={isSelected} title={`${kindLabel(entry.type, false)} ${entry.name}`} onClick={event => void page.graph.select(entry, isAlso(event))}>
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
  const rules = page.graph.rulesOf(entry)
  const isOpen = page.graph.isOpen(entry)
  return (
    <li className="graph-entry" data-kind={entry.type}>
      <GraphRowView page={page} entry={entry} hasBelow={below.length > 0 || rules.length > 0 || entry.children_left_out > 0} />
      {isOpen && (below.length || rules.length) ? (
        <ul>
          {rules.length ? <RulesView page={page} entry={entry} rules={rules} /> : null}
          {below.map(child => (
            <GraphEntryView key={child.node_id} page={page} entry={child} />
          ))}
        </ul>
      ) : null}
    </li>
  )
}

// The rules a node is judged by, under it as the Graph app shows them: one closed rules group, then each rule marked
// passing, broken or left to the agent's judgement. A broken rule's title carries its message, which a hover shows,
// selecting it opens the lines its violations name, and it offers Fix this one, for the rule on this node, and Fix rule,
// for the rule on every node the view shows.
function RulesView({ page, entry, rules }: { page: FilesPage; entry: ExplorerEntryData; rules: GraphRuleData[] }) {
  const [isOpen, setOpen] = useState(false)
  return (
    <li className="graph-entry" data-kind="Rules">
      <div className="tree-row">
        <button className="tree-twist" aria-expanded={isOpen} aria-label={`${isOpen ? 'Close' : 'Open'} rules`} onClick={() => setOpen(!isOpen)}>
          {isOpen ? '▼' : '▶'}
        </button>
        <span className="graph-node rules-group">
          <KindMark kind="Rules" isFile={false} />
          <span className="node-name">rules</span>
        </span>
      </div>
      {isOpen ? (
        <ul>
          {rules.map(rule => (
            <li key={rule.name} className="graph-entry" data-kind="Rule">
              <div className="tree-row">
                <span className="tree-twist-spacer" />
                <button className={`graph-node rule-status ${rule.status}`} title={ruleTitleOf(rule)} onClick={() => void page.graph.selectRule(entry, rule)}>
                  <KindMark kind="Rule" isFile={false} />
                  <span className="node-name">{rule.name}</span>
                </button>
                {isFailing(rule) ? (
                  <span className="graph-rule-fixes">
                    <FixButton label="Fix this one" title={`Send the fix of ${rule.name} on ${entry.name} to the chat that opened the page`} testId="graph-fix-one" fix={() => page.graph.fix({ rule: rule.name, nodeId: entry.node_id })} />
                    <FixButton label="Fix rule" title={`Send the fix of ${rule.name} on every node the graph view shows to the chat that opened the page`} testId="graph-fix-rule" fix={() => page.graph.fix({ rule: rule.name })} />
                  </span>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      ) : null}
    </li>
  )
}


// The graph view's node filter, the Graph app's lists: node types, connectors, rules and the Violations switch, which
// narrow the nodes of the files the bar lists, with Fix all beside them for every broken rule the view shows. They sit
// closed behind one Filters toggle, so the trees get the space, until the person opens them; this browser remembers the
// choice.
function GraphNodeFilterView({ page }: { page: FilesPage }) {
  const { graph } = useFilesState(page)
  const [isShown, setShown] = useState(() => page.graph.areFiltersShown)
  const toggle = () => {
    page.graph.showFilters(!isShown)
    setShown(!isShown)
  }
  return (
    <div className="graph-node-filter-bar">
      <button className="graph-filters-toggle" aria-expanded={isShown} onClick={toggle}>
        <span aria-hidden="true">{isShown ? '▼' : '▶'}</span> Filters
      </button>
      {graph.trees?.length ? <FixButton label="Fix all" title="Send the fix of every broken rule the graph view shows to the chat that opened the page" testId="graph-fix-all" fix={() => page.graph.fix()} /> : null}
      {isShown ? (
        <div className="filters graph-node-filter" aria-label="Node filter">
          <NodeFilterLists
            selection={graph.filter}
            nodeTypes={graph.choices.offered_node_types}
            relationships={graph.choices.relationships}
            rules={graph.choices.rules}
            onChange={next => void page.graph.filterTo(next)}
          />
        </div>
      ) : null}
    </div>
  )
}

// A graph read that failed: the server's reason in place of the trees, and Copy for AI, which puts it on the clipboard
// for the person to paste to the chat, as the Graph app offers.
function GraphProblemView({ page, problem }: { page: FilesPage; problem: string }) {
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(problem)
    } catch (cause) {
      page.notices.fail(`The failure was not copied: ${cause instanceof Error ? cause.message : String(cause)}`, 'Copy for AI in the Files app graph view')
    }
  }
  return (
    <div className="files-note graph-problem">
      <button type="button" className="copy-diagnosis" onClick={() => void copy()}>
        Copy for AI
      </button>
      <pre>{problem}</pre>
    </div>
  )
}

// The file bar's graph view: its node filter, closed until a person opens it, then the practice trees of the session's
// graph holding only the nodes of the files the bar lists that the filter keeps, each collapsed until a person opens it.
export function FilesGraphView({ page }: { page: FilesPage }) {
  const { graph } = useFilesState(page)
  return (
    <>
      <GraphNodeFilterView page={page} />
      <GraphTreesView page={page} graph={graph} />
    </>
  )
}

function GraphTreesView({ page, graph }: { page: FilesPage; graph: FilesGraphState }) {
  if (graph.problem) return <GraphProblemView page={page} problem={graph.problem} />
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
