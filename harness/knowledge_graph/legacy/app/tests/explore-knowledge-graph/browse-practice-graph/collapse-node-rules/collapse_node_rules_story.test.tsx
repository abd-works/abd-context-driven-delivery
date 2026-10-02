import { fireEvent, render } from '@testing-library/react';
import { story, scenario } from '../../../story-test';
import { PracticeGraphTree } from '../../../../packages/explore-knowledge-graph/PracticeGraphTree';
import { KnowledgeGraph } from '../../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { overlayWorkspaceTree } from '../../../../packages/explore-knowledge-graph/knowledge-graph/workspace-overlay';
import { SelectedNodePane } from '../../../../packages/explore-knowledge-graph/SelectedNodePane';
import { ExplorePracticeGraphsClientHelper } from '../../helpers/explore-practice-graphs.client';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../../helpers/explore-practice-graphs.base';
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
} from '../../helpers/story-graphs';

const helper = new ExplorePracticeGraphsClientHelper();

story('Collapse Node Rules', () => {
  scenario('rules stay collapsed until the rules Node is opened', ({ given, when, then }) => {
    given('a Node with applicable rules', async () => {
      await helper.seed();
      await helper.browse();
    });
    when('the Engineer expands that Node without opening rules', () => {});
    then('rule slugs are not listed', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expandNonRuleTwists(container);
      expect(container.textContent ?? '').not.toContain(KEEP_OPERATIONS_SMALL_FOCUSED);
    });
    when('the Engineer opens the rules child', () => {});
    then('those rules are listed', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      expandNonRuleTwists(container);
      const rulesTwist = container.querySelector('[data-testid="tree-expand-rules"]');
      expect(rulesTwist).not.toBeNull();
      fireEvent.click(rulesTwist!);
      expect(container.textContent ?? '').toContain(KEEP_OPERATIONS_SMALL_FOCUSED);
    });
  });
});
