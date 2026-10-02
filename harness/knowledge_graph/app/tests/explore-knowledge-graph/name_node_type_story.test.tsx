import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Name Node Type', () => {
  scenario('hover names the Node type', ({ given, when, then }) => {
    given('a Package and a Module on the PracticeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer points at the Node icon or name', async () => {
      await explorer().locator('.kind-mark').first().hover();
    });
    then('the tooltip names Package', async () => {
      await expect(explorer().locator('button[title="Package"]')).toBeVisible();
    }).and('names Module', async () => {
      await expect(explorer().locator('.kind-mark[aria-label="Module"]').first()).toBeVisible();
    });
  });
});
