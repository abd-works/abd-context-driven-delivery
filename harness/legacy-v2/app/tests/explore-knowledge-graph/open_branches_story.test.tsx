import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Open Branches', () => {
  scenario('branches stay closed until the Engineer opens them', ({ given, when, then }) => {
    given('pml-domain is loaded into the KnowledgeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer has not opened a branch', async () => {});
    then('Clean Engineering is closed', async () => {
      await expect(explorer().getByRole('button', { name: 'Expand Clean Engineering', exact: true })).toBeVisible();
    }).and('domain is not listed until that branch is opened', async () => {
      await expect(explorer().getByRole('button', { name: 'Module domain' })).toHaveCount(0);
      await expand('Clean Engineering');
      await expect(explorer().getByRole('button', { name: 'Expand domain', exact: true })).toBeVisible();
    });
  });

  scenario('an opened branch stays open on the next visit', ({ given, when, then }) => {
    given('pml-domain is loaded into the KnowledgeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer opens Clean Engineering and domain', async () => {
      await expand('Clean Engineering');
      await expand('domain');
      await explorer().reload();
      await waitForTree();
    });
    then('those branches are still open', async () => {
      await expect(explorer().getByRole('button', { name: 'Collapse Clean Engineering', exact: true })).toBeVisible();
      await expect(explorer().getByRole('button', { name: 'Collapse domain', exact: true })).toBeVisible();
    }).and('a branch that was not opened stays closed', async () => {
      await expect(explorer().getByRole('button', { name: 'Expand customer', exact: true }).first()).toBeVisible();
    });
  });
});
