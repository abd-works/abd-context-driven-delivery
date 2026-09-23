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

story('Show Disk Packages', () => {
  scenario('disk folders show under a Module even when they are only Packages', ({ given, when, then }) => {
    given('harness with disk folders guidance and mcp', () => {});
    when('the Engineer opens harness', () => {});
    then('those folders are listed', () => {
      const harness = KnowledgeGraph.fromDto(diskSubfolderGraph())
        .present()
        .listed_tree.find((node) => node.name === 'harness');
      expect(harness?.children.map((node) => node.name)).toEqual(['guidance', 'mcp']);
    }).and('classes stay inside them', () => {
      const harness = KnowledgeGraph.fromDto(diskSubfolderGraph())
        .present()
        .listed_tree.find((node) => node.name === 'harness');
      const guidance = harness?.children.find((node) => node.name === 'guidance');
      expect(guidance?.children.map((node) => node.name)).toContain('Guidance');
      expect(harness?.children.map((node) => node.name)).not.toContain('Guidance');
    });
  });
});
