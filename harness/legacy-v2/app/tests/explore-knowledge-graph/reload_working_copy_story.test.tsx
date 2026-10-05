import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, openPmlDomain, waitForTree, waitForWork } from './helpers/pml-domain';

bindPage();

story('Reload Working Copy', () => {
  scenario('reloading the working copy keeps the saved document', ({ given, when, then }) => {
    given('pml-domain is the working folder', async () => {
      await openPmlDomain();
    });
    when('the Engineer reloads the latest files into the working copy', async () => {
      await explorer().getByTestId('reload-working-copy').click();
      await waitForWork('Reload working copy');
    });
    then('the PracticeGraph lists domain', async () => {
      await waitForTree();
      await expand('Clean Engineering');
      await expect(explorer().getByRole('button', { name: 'Module domain' })).toBeVisible();
    });
  });
});
