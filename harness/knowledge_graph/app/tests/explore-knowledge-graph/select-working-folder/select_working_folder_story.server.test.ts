import { story, scenario } from '../../story-test';
import { ExplorePracticeGraphsServerHelper } from '../helpers/explore-practice-graphs.server';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsServerHelper();

story('Select Working Folder', () => {
  scenario('selecting a folder scans it into the KnowledgeGraph', ({ given, when, then }) => {
    given('a folder whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer selects that folder', async () => {
      await helper.selectFolder();
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
