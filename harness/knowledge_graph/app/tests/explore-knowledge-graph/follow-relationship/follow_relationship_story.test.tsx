import { fireEvent, render } from '@testing-library/react';
import { story, scenario } from '../../story-test';
import { PracticeGraphTree } from '../../../packages/explore-knowledge-graph/PracticeGraphTree';
import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { RELATIONSHIP_KINDS } from '../../../packages/explore-knowledge-graph/knowledge-graph/catalog';
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
  classDemonstratedThroughExampleGraph,
} from '../helpers/story-graphs';

function customerRow(container: HTMLElement) {
  const name = [...container.querySelectorAll('.tree-name')].find(
    (node) => node.textContent === 'Customer',
  );
  return name?.closest('li') as HTMLElement;
}

const helper = new ExplorePracticeGraphsClientHelper();

story('Follow Relationship', () => {
  scenario('following a Relationship focuses the target Node', ({ given, when, then }) => {
    given('a Node with a Relationship to a target Node', async () => {
      await helper.seed();
    });
    when('the Engineer follows the Relationship', async () => {
      await helper.followRelationship(passingLoadOperation.node_id);
    });
    then('the target Node is selected', () => {
      expect(helper.listed?.selected_node?.node_id).toBe(passingLoadOperation.node_id);
    }).and('the target source file is shown when the target is a file', () => {
      expect(helper.listed?.source_file?.file).toBe('domain/customer/Customer.ts');
    });
  });

  scenario('a Class lists Relationship kinds including demonstratedThrough', ({ given, when, then }) => {
    let selectedId: string | null = null;
    given('a Class Node demonstrated through a stories Example', () => {
      selectedId = null;
    });
    when('the Engineer opens relationships on that Class', () => {});
    then('every Relationship kind is listed', () => {
      const tree = KnowledgeGraph.fromDto(
        classDemonstratedThroughExampleGraph(),
      ).present().listed_tree;
      const customer = findTreeNode(tree, 'Customer');
      expect(customer?.relationships.map((group) => group.kind)).toEqual([
        ...RELATIONSHIP_KINDS,
      ]);
      const { container } = render(
        <PracticeGraphTree
          roots={tree}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expandNonRuleTwists(container);
      const row = customerRow(container);
      expect(row.textContent ?? '').not.toContain('demonstratedThrough');
      fireEvent.click(row.querySelector('[data-testid="tree-expand-relationships"]')!);
      expect(row.textContent ?? '').toContain('demonstratedThrough');
      for (const kind of RELATIONSHIP_KINDS) {
        expect(row.textContent ?? '').toContain(kind);
      }
    }).and('demonstratedThrough lists the Example', () => {
      const tree = KnowledgeGraph.fromDto(
        classDemonstratedThroughExampleGraph(),
      ).present().listed_tree;
      const customer = findTreeNode(tree, 'Customer');
      const through = customer?.relationships.find(
        (group) => group.kind === 'demonstratedThrough',
      );
      expect(through?.targets.map((target) => target.name)).toEqual(['adder']);
    });
    when('the Engineer follows demonstratedThrough to that Example', () => {});
    then('the Example Node is selected', () => {
      const tree = KnowledgeGraph.fromDto(
        classDemonstratedThroughExampleGraph(),
      ).present().listed_tree;
      const { container } = render(
        <PracticeGraphTree
          roots={tree}
          selectedId={selectedId}
          onSelect={(id) => {
            selectedId = id;
          }}
        />,
      );
      expandNonRuleTwists(container);
      const customer = customerRow(container);
      fireEvent.click(customer.querySelector('[data-testid="tree-expand-relationships"]')!);
      const through = [...customer.querySelectorAll(
        '[data-testid="tree-expand-relationship-kind"]',
      )].find((button) =>
        button.getAttribute('aria-label')?.includes('demonstratedThrough'),
      );
      fireEvent.click(through!);
      fireEvent.click(customer.querySelector('[data-testid="tree-relationship-target"]')!);
      expect(selectedId).toBe('st:Example:adder');
    });
  });
});
