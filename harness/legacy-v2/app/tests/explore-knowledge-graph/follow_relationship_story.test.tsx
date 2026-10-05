import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, openFolder, RULE_OUTCOMES, waitForTree } from './helpers/pml-domain';

bindPage();

story('Follow Relationship', () => {
  scenario('following a Relationship focuses the target Node', ({ given, when, then }) => {
    given('a Node with a Relationship to a target Node', async () => {
      await openFolder(RULE_OUTCOMES);
      await waitForTree('Clean Engineering');
    });
    when('the Engineer follows the Relationship', async () => {
      await expand('Clean Engineering');
      await expand('orders');
      await expand('Order');
      await explorer().locator('.node-name', { hasText: /^processEverything$/ }).first().click({ timeout: 5_000 });
    });
    then('the target Node is selected', async () => {
      await expect(
        explorer().locator('[data-node-id].is-selected').filter({ hasText: 'processEverything' }),
      ).toBeVisible();
    }).and('the target source file is shown when the target is a file', async () => {
      await expect(explorer().getByTestId('source-file')).toContainText('processEverything');
      await expect(explorer().locator('.monaco-editor').first()).toBeVisible({ timeout: 20_000 });
    }).and('the Node stays in the tree', async () => {
      await expect(
        explorer().getByTestId('practice-graph-tree').locator('[data-node-id].is-selected'),
      ).toBeVisible();
    });
  });
});
