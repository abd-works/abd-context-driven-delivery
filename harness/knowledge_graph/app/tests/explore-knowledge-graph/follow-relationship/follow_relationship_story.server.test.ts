import { story, scenario } from '../../story-test';
import { KnowledgeGraph } from '../../../packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { RELATIONSHIP_KINDS } from '../../../packages/explore-knowledge-graph/knowledge-graph/catalog';
import { ExplorePracticeGraphsServerHelper } from '../helpers/explore-practice-graphs.server';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../helpers/explore-practice-graphs.base';
import {
  classDemonstratedThroughExampleGraph,
  findTreeNode,
} from '../helpers/story-graphs';

const helper = new ExplorePracticeGraphsServerHelper();

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
    given('a Class Node demonstrated through a stories Example', () => {});
    when('the Engineer opens relationships on that Class', () => {});
    then('every Relationship kind is listed', () => {
      const customer = findTreeNode(
        KnowledgeGraph.fromDto(classDemonstratedThroughExampleGraph()).present()
          .listed_tree,
        'Customer',
      );
      expect(customer?.relationships.map((group) => group.kind)).toEqual([
        ...RELATIONSHIP_KINDS,
      ]);
    }).and('demonstratedThrough lists the Example', () => {
      const customer = findTreeNode(
        KnowledgeGraph.fromDto(classDemonstratedThroughExampleGraph()).present()
          .listed_tree,
        'Customer',
      );
      const through = customer?.relationships.find(
        (group) => group.kind === 'demonstratedThrough',
      );
      expect(through?.targets.map((target) => target.name)).toEqual(['adder']);
    });
    when('the Engineer follows demonstratedThrough to that Example', () => {});
    then('the Example Node is selected', () => {
      const selected = KnowledgeGraph.fromDto(
        classDemonstratedThroughExampleGraph(),
      )
        .followRelationship('st:Example:adder')
        .present();
      expect(selected.selected_node?.node_id).toBe('st:Example:adder');
      expect(selected.source_file?.file).toBe(
        'practices/stories/catalog-examples/adder.ts',
      );
    });
  });
});
