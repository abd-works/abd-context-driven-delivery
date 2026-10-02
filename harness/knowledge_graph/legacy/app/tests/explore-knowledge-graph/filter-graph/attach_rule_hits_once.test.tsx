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

story('Attach Rule Hits Once', () => {
  scenario('a cloned __init__ hit is not listed on every constructor', ({ given, when, then }) => {
    const dto = clonedInitHits();
    given('two __init__ operations carrying the same keep-operations-small-focused message', () => {
      KnowledgeGraph.fromDto(dto);
    });
    when('the Engineer browses the KnowledgeGraph', () => {});
    then('the four-line constructor does not list that hit', () => {
      const host = dto.practice_graphs[0]?.nodes.find((node) => node.node_id === 'op:host-init');
      expect(host?.violations).toEqual([]);
    }).and('the constructor named in the message still lists it', () => {
      const stories = dto.practice_graphs[0]?.nodes.find(
        (node) => node.node_id === 'op:stories-init',
      );
      expect(stories?.violations).toHaveLength(1);
    });
  });

  scenario('a Function hide-inner-details hit is not listed on Parameters named name', ({ given, when, then }) => {
    const dto = clonedNameParameterHits();
    given('two name Parameters carrying the same hide-inner-details message', () => {
      KnowledgeGraph.fromDto(dto);
    });
    when('the Engineer browses the KnowledgeGraph', () => {});
    then('neither Parameter keeps the cloned hit', () => {
      const names = dto.practice_graphs[0]?.nodes.filter((node) => node.name === 'name') ?? [];
      expect(names.every((node) => node.violations.length === 0)).toBe(true);
    });
  });
});
