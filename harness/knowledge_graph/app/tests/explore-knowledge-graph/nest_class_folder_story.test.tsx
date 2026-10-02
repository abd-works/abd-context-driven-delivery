import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Nest Class Folder', () => {
  scenario('classes sit in their subfolder', ({ given, when, then }) => {
    given('pml-domain has a customer folder and a Customer class', async () => {
      await openPmlDomain();
    });
    when('the Engineer browses the KnowledgeGraph', async () => {
      await waitForTree();
    });
    then('customer sits under domain', async () => {
      const domain = explorer().locator('li[data-depth="0"]').filter({ hasText: 'domain' }).first();
      await expect(domain.locator('.node-name', { hasText: /^customer$/ })).toBeVisible();
    }).and('Customer sits under customer', async () => {
      const customer = explorer()
        .locator('li')
        .filter({ has: explorer().locator('.node-name', { hasText: /^customer$/ }) })
        .first();
      await expect(customer.locator('.node-name', { hasText: /^Customer$/ })).toBeVisible();
    });
  });
});
