import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Open Node Source', () => {
  scenario('file Node opens source and highlights range', ({ given, when, then }) => {
    given('a KnowledgeGraph with a file Node that has a source file and range', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer selects the file Node', async () => {
      await explorer().locator('[data-node-id]').filter({ hasText: /^Customer$/ }).first().click();
    });
    then('the source file is shown', async () => {
      await expect(explorer().getByTestId('source-excerpt')).toBeVisible();
    }).and('the Node range is highlighted', async () => {
      await expect(explorer().locator('.source-highlight')).toBeVisible();
    });
  });

  scenario('class Node shows the whole class', ({ given, when, then }) => {
    given('a class Node whose graph source is missing or only the header', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer selects the class Node', async () => {
      await explorer().locator('[data-node-id]').filter({ hasText: /^Customer$/ }).first().click();
    });
    then('the source pane shows the whole class body', async () => {
      const body = explorer().getByTestId('source-file').locator('.panel-source');
      await expect(body).toContainText('class');
      await expect(body).not.toHaveText(/^Customer$/);
    }).and('rule problems sit below that excerpt', async () => {
      await expect(explorer().getByTestId('source-file').locator('.rule-status')).toBeVisible();
    });
  });
});
