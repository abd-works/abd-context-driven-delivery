import { KEEP_OPERATIONS_SMALL_FOCUSED, type KnowledgeGraph } from '../../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import {
  failingProcessEverythingOperation,
  passingLoadOperation,
  seededKnowledgeGraph,
  SEEDED_GRAPH_ID,
  FIXTURE_WORKSPACE,
} from '../examples/knowledge-graph.examples';

export {
  failingProcessEverythingOperation,
  KEEP_OPERATIONS_SMALL_FOCUSED,
  passingLoadOperation,
  seededKnowledgeGraph,
  SEEDED_GRAPH_ID,
  FIXTURE_WORKSPACE,
};

export abstract class ExplorePracticeGraphsBaseHelper {
  protected graph: KnowledgeGraph | null = null;
  listed: ReturnType<KnowledgeGraph['present']> | null = null;

  protected abstract seed(): Promise<void>;
  abstract cleanup(): Promise<void>;

  passingNode() {
    return this.listed?.listed_nodes.find((node) => node.name === passingLoadOperation.name);
  }

  failingNode() {
    return this.listed?.listed_nodes.find(
      (node) => node.name === failingProcessEverythingOperation.name,
    );
  }
}
