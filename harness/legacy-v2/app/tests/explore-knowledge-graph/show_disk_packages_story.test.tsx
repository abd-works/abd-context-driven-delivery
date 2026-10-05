import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Show Disk Packages', () => {
  scenario('disk folders show under a Module even when they are only Packages', ({ given, when, then }) => {
    given('domain has disk folders on disk', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer opens domain', async () => {
      await expand('Clean Engineering');
      await expand('domain');
    });
    then('those folders are listed', async () => {
      await expect(explorer().locator('button[title="Package"]', { hasText: 'customer' })).toBeVisible();
    }).and('classes stay inside them', async () => {
      const folder = explorer().locator('li').filter({ has: explorer().locator('button[title="Package"]', { hasText: /^customer$/ }) }).first();
      await expect(folder.locator('.node-name', { hasText: /^Customer$/ })).toBeVisible();
    });
  });
});
