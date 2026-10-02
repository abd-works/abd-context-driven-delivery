import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Open Node Source', () => {
  scenario('file Node opens source', ({ given, when, then }) => {
    given('a KnowledgeGraph with a Customer Node that has source', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer selects the Customer Node', async () => {
      await explorer().locator('[data-node-id]').filter({ hasText: /^Customer$/ }).first().click();
    });
    then('the source is shown', async () => {
      await expect(
        explorer().locator('.knowledge-graph-panel, [data-testid="source-file"]'),
      ).toContainText(/Customer|class/);
    });
  });
});
