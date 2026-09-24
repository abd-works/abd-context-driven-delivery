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
  fileParkingLotGraph,
} from '../../helpers/story-graphs';

const helper = new ExplorePracticeGraphsClientHelper();

story('Nest Class Folder', () => {
  scenario('classes sit in their subfolder, not the parent Module', ({ given, when, then }) => {
        given('catalog folder harness that contains Module guidance under harness/guidance', () => {});
        when('the Engineer opens harness', () => {});
        then('harness children include the guidance folder', () => {
          const harness = KnowledgeGraph.fromDto(nestedClassGraph())
            .present()
            .listed_tree.find((node) => node.name === 'harness');
          expect(harness?.children.map((node) => node.name)).toEqual(['guidance']);
        }).and('do not list Guidance as a direct child', () => {
          const harness = KnowledgeGraph.fromDto(nestedClassGraph())
            .present()
            .listed_tree.find((node) => node.name === 'harness');
          expect(harness?.children.map((node) => node.name)).not.toContain('Guidance');
          expect(descendantNames(harness)).toContain('Guidance');
        }).and('harness is a Package', () => {
          const harness = KnowledgeGraph.fromDto(nestedClassGraph())
            .present()
            .listed_tree.find((node) => node.name === 'harness');
          expect(harness?.semantic_type).toBe('Package');
        });
  });
  scenario('a class lists its operations', ({ given, when, then }) => {
    given('a class Node that owns operations', () => {});
    when('the Engineer opens the class in the PracticeGraph', () => {});
    then('the class children include those operations', () => {
      const tree = KnowledgeGraph.fromDto(
        overlayWorkspaceTree(codeQlClassWithoutSource()),
      ).present().listed_tree;
      const customer = findTreeNode(tree, 'Customer');
      expect(customer?.children.map((node) => node.name)).toContain(
        'processEverything',
      );
    }).and('still nest them when owns points at the class', () => {
      const dto = codeQlClassWithoutSource();
      dto.practice_graphs[0]?.relationships.push({
        kind: 'owns',
        from_id: 'ce:Operation:processEverything',
        to_id: 'ce:OoadClass:Customer',
      });
      const tree = KnowledgeGraph.fromDto(overlayWorkspaceTree(dto)).present()
        .listed_tree;
      const customer = findTreeNode(tree, 'Customer');
      expect(customer?.children.map((node) => node.name)).toContain(
        'processEverything',
      );
    });
  });
  scenario('classless members sit on the package, not a File', ({ given, when, then }) => {
    given('a package whose file owns a class and a classless operation', () => {});
    when('the Engineer opens that package', () => {});
    then('the package children include the class and the classless operation', () => {
      const grill = findTreeNode(
        KnowledgeGraph.fromDto(fileParkingLotGraph()).present().listed_tree,
        'grill_context',
      );
      expect(grill?.children.map((node) => node.name)).toEqual(
        expect.arrayContaining(['GrillContext', 'ask']),
      );
    }).and('do not list the file', () => {
      const grill = findTreeNode(
        KnowledgeGraph.fromDto(fileParkingLotGraph()).present().listed_tree,
        'grill_context',
      );
      expect(grill?.children.map((node) => node.name)).not.toContain(
        'actions/grill_context/grill_context.py',
      );
      expect(grill?.children.map((node) => node.semantic_type)).not.toContain(
        'File',
      );
    }).and('do not list a module variable as a Property', () => {
      const grill = findTreeNode(
        KnowledgeGraph.fromDto(fileParkingLotGraph()).present().listed_tree,
        'grill_context',
      );
      expect(grill?.children.map((node) => node.name)).not.toContain('ROOT');
      expect(grill?.children.map((node) => node.semantic_type)).not.toContain(
        'Property',
      );
    });
  });
});
