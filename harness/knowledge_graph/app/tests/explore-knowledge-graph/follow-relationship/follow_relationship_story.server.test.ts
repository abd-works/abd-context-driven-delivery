import { story, scenario } from '../../story-test';
import { ExplorePracticeGraphsServerHelper } from '../helpers/explore-practice-graphs.server';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../helpers/explore-practice-graphs.base';

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
});
