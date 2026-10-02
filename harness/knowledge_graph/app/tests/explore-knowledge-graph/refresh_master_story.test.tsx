import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree, waitForWork } from './helpers/pml-domain';

bindPage();

story('Refresh Master', () => {
  scenario('refreshing master keeps the saved document', ({ given, when, then }) => {
    given('pml-domain is the working folder', async () => {
      await openPmlDomain();
    });
    when('the Engineer refreshes master', async () => {
      await explorer().getByTestId('refresh-master').click();
      await waitForWork('Refresh master');
    });
    then('the PracticeGraph lists domain', async () => {
      await waitForTree();
    });
  });
});
