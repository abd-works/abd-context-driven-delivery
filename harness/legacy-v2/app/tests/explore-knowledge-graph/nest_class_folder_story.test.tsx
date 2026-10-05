import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Nest Class Folder', () => {
  scenario('classes sit in their subfolder, not the parent Module', ({ given, when, then }) => {
    given('Module domain that owns class Customer under domain/customer', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer opens domain', async () => {
      await expand('Clean Engineering');
      await expand('domain');
    });
    then('domain children include the customer folder', async () => {
      const domain = explorer().locator('li[data-depth="0"]').filter({ hasText: 'domain' }).first();
      await expect(domain.locator(':scope > ul > li .node-name', { hasText: /^customer$/ })).toBeVisible();
    }).and('do not list Customer as a direct child', async () => {
      const domain = explorer().locator('li[data-depth="0"]').filter({ hasText: 'domain' }).first();
      await expect(domain.locator(':scope > ul > li > .tree-row .node-name', { hasText: /^Customer$/ })).toHaveCount(0);
    }).and('the customer folder lists the Customer class', async () => {
      await explorer().getByRole('button', { name: 'Expand customer', exact: true }).first().click();
      const folder = explorer().locator('li').filter({
        has: explorer().getByRole('button', { name: 'customer', exact: true }),
      }).first();
      await expect(folder.locator('button[title="Class"]', { hasText: /^Customer$/ }).first()).toBeVisible();
      await explorer().getByRole('button', { name: 'Expand Customer', exact: true }).first().click();
      await expect(folder.locator('button[title="Property"]', { hasText: /^kycVerified$/ }).first()).toBeVisible();
      await explorer().getByRole('button', { name: 'Expand AccountCredentialsE2e', exact: true }).first().click();
      await expect(folder.locator('button[title="Operation"]', { hasText: /^validate$/ }).first()).toBeVisible();
      await expect(folder.locator('button[title="Property"]', { hasText: /^email$/ }).first()).toBeVisible();
    });
  });
});
