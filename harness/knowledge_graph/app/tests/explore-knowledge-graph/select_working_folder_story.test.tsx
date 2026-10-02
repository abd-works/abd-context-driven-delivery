import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, RULE_OUTCOMES, waitForTree } from './helpers/pml-domain';

bindPage();

story('Select Working Folder', () => {
  scenario('selecting a repo folder loads the Knowledge Graph', ({ given, when, then }) => {
    given('a folder whose source includes a Node that passes keep-operations-small-focused', async () => {
      await openPmlDomain();
      await waitForTree();
    }).and('whose source includes a Node that fails keep-operations-small-focused', async () => {});
    when('the Engineer selects that folder', async () => {
      const chosen = explorer().getByTestId('chosen-folder');
      await chosen.fill(RULE_OUTCOMES);
      await chosen.press('Enter');
      await waitForTree('processEverything');
      await explorer().getByRole('button', { name: 'Show rules' }).click({ timeout: 5_000 });
    });
    then('the passing Node lists keep-operations-small-focused as passing', async () => {
      await expect(
        explorer().locator('.rule-status.passing', { hasText: 'keep-operations-small-focused' }),
      ).toBeVisible();
    }).and('the failing Node lists keep-operations-small-focused as violating', async () => {
      await expect(
        explorer().locator('.rule-status.violating', { hasText: 'keep-operations-small-focused' }),
      ).toBeVisible();
    }).and('the chosen folder is the selected repository', async () => {
      await expect(explorer().getByTestId('chosen-folder')).toHaveValue(RULE_OUTCOMES);
    });
  });
});
