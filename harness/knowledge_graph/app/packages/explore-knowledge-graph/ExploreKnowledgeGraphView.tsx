import { KnowledgeGraphExplorerView } from './knowledge-graph/knowledge-graph-client';

/**
 * ExploreKnowledgeGraphView — feature view.
 * Sources: harness/knowledge_graph/.context/knowledge-graph-explorer-sketch.md
 */
export function ExploreKnowledgeGraphView({ graphId = '' }: { graphId?: string }) {
  return (
    <main className="explore-knowledge-graph">
      <KnowledgeGraphExplorerView graphId={graphId} />
    </main>
  );
}
