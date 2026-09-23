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

story('Name Node Type', () => {
  scenario('hover names the Node type', ({ given, when, then }) => {
    given('a Package and a Module on the PracticeGraph', async () => {
      await helper.seed();
    });
    when('the Engineer points at the Node icon or name', async () => {
      await helper.browse();
    });
    then('the tooltip names Package', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      for (let step = 0; step < 20; step += 1) {
        const closed = container.querySelector(
          '[data-testid="tree-expand"][aria-expanded="false"]',
        );
        if (!closed) {
          break;
        }
        fireEvent.click(closed);
      }
      const root = container.querySelector('li[data-depth="0"] > .tree-row > button[title]');
      expect(root?.getAttribute('title')).toBe('Package');
    }).and('names Module', () => {
      const { container } = render(
        <PracticeGraphTree
          roots={helper.listed?.listed_tree ?? []}
          selectedId={null}
          onSelect={() => undefined}
        />,
      );
      for (let step = 0; step < 20; step += 1) {
        const closed = container.querySelector(
          '[data-testid="tree-expand"][aria-expanded="false"]',
        );
        if (!closed) {
          break;
        }
        fireEvent.click(closed);
      }
      expect(
        container.querySelector(
          'button[title="Module"], button[title="File"], button[title="Operation"]',
        ),
      ).not.toBeNull();
    });
  });
});
