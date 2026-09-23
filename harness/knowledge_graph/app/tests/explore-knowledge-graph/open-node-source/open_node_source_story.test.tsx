import { fireEvent, render } from '@testing-library/react';
import { story, scenario } from '../../story-test';
import { PracticeGraphTree } from '../../../packages/explore-knowledge-graph/PracticeGraphTree';
import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { overlayWorkspaceTree } from '../../../packages/explore-knowledge-graph/knowledge-graph/workspace-overlay';
import { SelectedNodePane } from '../../../packages/explore-knowledge-graph/SelectedNodePane';
import { ExplorePracticeGraphsClientHelper } from '../helpers/explore-practice-graphs.client';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../helpers/explore-practice-graphs.base';
import {
  expandNonRuleTwists,
  treeNames,
  findTreeNode,
  descendantNames,
  clonedNameParameterHits,
  clonedInitHits,
  diskSubfolderGraph,
  nestedClassGraph,
  codeQlClassWithoutSource,
  violatingClassWithPassingOps,
} from '../helpers/story-graphs';

const helper = new ExplorePracticeGraphsClientHelper();

story('Open Node Source', () => {
  scenario('file Node opens source and highlights range', ({ given, when, then }) => {
    given('a KnowledgeGraph with a file Node that has a source file and range', async () => {
      await helper.seed();
    });
    when('the Engineer selects the file Node', async () => {
      await helper.selectNode(passingLoadOperation.node_id);
    });
    then('the source file is shown', () => {
      expect(helper.listed?.source_file?.file).toBe(passingLoadOperation.source?.file);
    }).and('the Node range is highlighted', () => {
      expect(helper.listed?.source_file?.start_line).toBe(
        passingLoadOperation.source?.start_line,
      );
    });
  });
  scenario('class Node shows the whole class', ({ given, when, then }) => {
    given('a class Node whose graph source is missing or only the header', () => {});
    when('the Engineer selects the class Node', () => {});
    then('the source pane shows the whole class body', () => {
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      ).selectNode('ce:OoadClass:Customer');
      const source = graph.present().source_file;
      expect(source?.text).toContain('export class Customer');
      expect(source?.text).toContain('processEverything');
      expect(source?.end_line).toBeGreaterThan(source?.start_line ?? 0);
    }).and('rule problems sit below that excerpt', () => {
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      ).selectNode('ce:OoadClass:Customer');
      const presented = graph.present();
      const { getByTestId } = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      const excerpt = getByTestId('source-excerpt');
      const nested = getByTestId('child-node-report');
      expect(excerpt.compareDocumentPosition(nested) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
      expect(nested.textContent).toContain('processEverything');
    });
  });
  scenario('operation Node shows the whole operation', ({ given, when, then }) => {
    given('an operation Node whose graph source is missing or only the header', () => {});
    when('the Engineer selects the operation Node', () => {});
    then('the source pane shows the whole operation', () => {
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      ).selectNode('ce:Operation:processEverything');
      const source = graph.present().source_file;
      expect(source?.text).toContain('processEverything');
      expect(source?.text).toContain('return u');
    }).and('not a slice that starts in another operation', () => {
      const dto = codeQlClassWithoutSource();
      const operation = dto.practice_graphs[0]?.nodes.find(
        (node) => node.node_id === 'ce:Operation:processEverything',
      );
      if (operation) {
        operation.source = {
          file: 'domain/customer/Customer.ts',
          start_line: 2,
          end_line: 8,
          text: '',
        };
      }
      const graph = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(dto),
      ).selectNode('ce:Operation:processEverything');
      const source = graph.present().source_file;
      expect(source?.text).toContain('processEverything');
      expect(source?.text).not.toContain('load(');
      expect(source?.start_line).toBe(6);
    });
  });
  scenario('a class pane lists nested operations', ({ given, when, then }) => {
    given('a class Node that owns operations', () => {});
    when('the Engineer selects the class Node', () => {});
    then('the source pane lists those operations under the class', () => {
      const presented = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      )
        .selectNode('ce:OoadClass:Customer')
        .present();
      expect(
        presented.selected_tree?.children.map((node) => node.name),
      ).toContain('processEverything');
      const { getByTestId } = render(
        <SelectedNodePane
          selectedNode={presented.selected_node}
          selectedTree={presented.selected_tree}
          selectedRule={null}
          sourceFile={presented.source_file}
        />,
      );
      expect(getByTestId('selected-subtree').textContent).toContain(
        'processEverything',
      );
    });
  });
});
