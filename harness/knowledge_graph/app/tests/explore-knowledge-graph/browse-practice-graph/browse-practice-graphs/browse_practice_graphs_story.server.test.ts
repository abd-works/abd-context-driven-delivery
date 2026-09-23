import { story, scenario } from '../../../story-test';
import { ExplorePracticeGraphsServerHelper } from '../../helpers/explore-practice-graphs.server';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../../helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsServerHelper();

story('Browse Practice Graphs', () => {
  scenario('KnowledgeGraph lists PracticeGraphs and Nodes', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer browses the KnowledgeGraph', async () => {
      await helper.browse();
    });
    then('the passing Node lists keep-operations-small-focused as passing', () => {
      expect(helper.passingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'passing',
      );
    }).and('the failing Node lists keep-operations-small-focused as violating', () => {
      expect(helper.failingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'violating',
      );
    });
  });
});
