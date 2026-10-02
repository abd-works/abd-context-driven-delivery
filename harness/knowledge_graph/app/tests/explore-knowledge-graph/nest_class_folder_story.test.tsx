import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Nest Class Folder', () => {
  scenario('classes sit in their subfolder, not the parent Module', ({ given, when, then }) => {
    given('Module domain that owns class Customer under domain/customer', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer opens domain', async () => {
      await explorer().getByRole('button', { name: 'Expand domain' }).click();
    });
    then('domain children include the customer folder', async () => {
      const domain = explorer().locator('li[data-depth="0"]').filter({ hasText: 'domain' }).first();
      await expect(domain.locator(':scope > ul > li .node-name', { hasText: /^customer$/ })).toBeVisible();
    }).and('do not list Customer as a direct child', async () => {
      const domain = explorer().locator('li[data-depth="0"]').filter({ hasText: 'domain' }).first();
      await expect(domain.locator(':scope > ul > li > .tree-row .node-name', { hasText: /^Customer$/ })).toHaveCount(0);
    });
  });
});
