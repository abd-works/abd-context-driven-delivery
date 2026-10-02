import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Follow Relationship', () => {
  scenario('following a Relationship focuses the target Node', ({ given, when, then }) => {
    given('a Node with a relationship to Customer', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer follows the relationship to Customer', async () => {
      await explorer().locator('[data-node-id]').filter({ hasText: /^Customer$/ }).first().click();
    });
    then('the target Node is selected', async () => {
      await expect(
        explorer().locator('[data-node-id].is-selected').filter({ hasText: /^Customer$/ }),
      ).toBeVisible();
    }).and('the target source is shown', async () => {
      await expect(explorer().getByTestId('source-file')).toContainText(/Customer|class/);
    }).and('the Node stays in the tree', async () => {
      await expect(
        explorer().getByTestId('practice-graph-tree').locator('[data-node-id].is-selected'),
      ).toBeVisible();
    });
  });
});
