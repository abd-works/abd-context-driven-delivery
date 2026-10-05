import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, openPmlDomain, waitForTree, waitForWork } from './helpers/pml-domain';

bindPage();

story('Merge Working Copy To Master', () => {
  scenario('merging the working copy writes it onto master', ({ given, when, then }) => {
    given('pml-domain is the working folder', async () => {
      await openPmlDomain();
    });
    when('the Engineer merges the working copy into master', async () => {
      await explorer().getByRole('button', { name: 'Merge working to master' }).click();
      await waitForWork('Merge working to master');
    });
    then('the PracticeGraph lists domain', async () => {
      await waitForTree();
      await expand('Clean Engineering');
      await expect(explorer().getByRole('button', { name: 'Module domain' })).toBeVisible();
    });
  });
});
