import { story, scenario } from '../../story-test';
import { ExplorePracticeGraphsServerHelper } from '../helpers/explore-practice-graphs.server';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from '../helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsServerHelper();

story('Open Node Source', () => {
  scenario('file Node opens source and highlights range', ({ given, when, then }) => {
    given('a KnowledgeGraph with a file Node that has a source file and range', async () => {
      await helper.seed();
    });
    when('the Engineer selects the file Node', async () => {
      await helper.selectNode(passingLoadOperation.node_id);
    });
    then('the source file is shown', () => {
      expect(helper.listed?.source_file?.file).toBe(passingLoadOperation.source?.file);
    }).and('the Node range is highlighted', () => {
      expect(helper.listed?.source_file?.start_line).toBe(
        passingLoadOperation.source?.start_line,
      );
      expect(helper.listed?.source_file?.end_line).toBe(
        passingLoadOperation.source?.end_line,
      );
    });
  });
});
