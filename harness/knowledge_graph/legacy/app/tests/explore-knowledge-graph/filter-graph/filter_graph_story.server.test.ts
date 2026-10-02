import { story, scenario } from '../../story-test';
import { ExplorePracticeGraphsServerHelper } from '../helpers/explore-practice-graphs.server';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsServerHelper();

story('Filter Graph', () => {
  scenario('tree lists only Nodes that match the filters', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer filters the KnowledgeGraph using violations', async () => {
      await helper.filterGraph();
    }).and('using keep-operations-small-focused', async () => {});
    then('the failing Node is listed', () => {
      expect(helper.failingNode()?.node_id).toBe(
        failingProcessEverythingOperation.node_id,
      );
    }).and('the passing Node is not listed', () => {
      expect(helper.passingNode()).toBeUndefined();
    }).and('ancestors of the failing Node remain', () => {
      const names: string[] = [];
      const walk = (nodes: { name: string; children: { name: string; children: never[] }[] }[]) => {
        for (const node of nodes) {
          names.push(node.name);
          walk(node.children);
        }
      };
      walk(helper.listed?.listed_tree ?? []);
      expect(names).toContain('processEverything');
      expect(names).toContain('domain');
      expect(names).not.toContain('load');
    });
  });
});
