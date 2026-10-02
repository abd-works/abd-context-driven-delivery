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

story('Indent Practice Graph', () => {
  scenario('children sit one indent level under their parent', ({ given, when, then }) => {
    given('a KnowledgeGraph with a parent Node and a child Node', async () => {
      await helper.seed();
    });
    when('the Engineer browses the KnowledgeGraph', async () => {
      await helper.browse();
    });
    then('the child sits one indent level under the parent', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      const parent = container.querySelector('li[data-depth="0"]');
      expect(parent?.querySelector('li[data-depth="1"]')).not.toBeNull();
    });
  });
});
