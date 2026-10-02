import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Name Node Type', () => {
  scenario('hover names the Node type', ({ given, when, then }) => {
    given('a Module on the PracticeGraph', async () => {
      await openPmlDomain();
    });
    when('the Engineer points at the Node', async () => {
      await waitForTree();
    });
    then('the Node names Module', async () => {
      await expect(explorer().locator('[data-kind="Module"]').first()).toBeVisible();
    });
  });
});
