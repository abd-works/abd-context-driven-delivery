import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openFolder, RULE_OUTCOMES, waitForTree } from './helpers/pml-domain';

bindPage();

story('Open Node Source', () => {
  scenario('file Node opens source and highlights range', ({ given, when, then }) => {
    given('a KnowledgeGraph with a file Node that has a source file and range', async () => {
      await openFolder(RULE_OUTCOMES);
      await waitForTree('orders');
    });
    when('the Engineer selects the file Node', async () => {
      await explorer().locator('[data-node-id]').filter({ hasText: /^processEverything$/ }).first().click();
    });
    then('the source file is shown', async () => {
      await expect(explorer().getByTestId('source-excerpt')).toBeVisible();
      await expect(explorer().locator('.monaco-editor').first()).toBeVisible({ timeout: 20_000 });
    }).and('the Node range is highlighted', async () => {
      await expect(explorer().locator('.source-highlight').first()).toBeVisible({ timeout: 20_000 });
    });
  });

  scenario('operation Node shows the whole operation', ({ given, when, then }) => {
    given('an operation Node whose source is the operation body', async () => {
      await openFolder(RULE_OUTCOMES);
      await waitForTree('orders');
    });
    when('the Engineer selects the operation Node', async () => {
      await explorer().locator('[data-node-id]').filter({ hasText: /^processEverything$/ }).first().click();
    });
    then('the source pane shows the whole operation', async () => {
      const body = explorer().getByTestId('source-file').locator('.panel-source');
      await expect(body).toContainText('processEverything', { timeout: 20_000 });
      await expect(body).toContainText('return step23');
      await expect(body).not.toHaveText(/^processEverything$/);
    }).and('rule problems sit below that excerpt', async () => {
      await expect(explorer().getByTestId('source-file').locator('.rule-status')).toBeVisible();
    });
  });
});
