import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Collapse Node Rules', () => {
  scenario('rules stay collapsed until the Node is expanded', ({ given, when, then }) => {
    given('a Node with applicable rules', async () => {
      await openPmlDomain();
      await waitForTree();
      await explorer().getByRole('button', { name: 'Show rules' }).click({ timeout: 5_000 });
    });
    when('the Engineer expands that Node without opening rules', async () => {
      await explorer().getByRole('button', { name: /^Expand / }).first().click({ timeout: 5_000 });
    });
    then('rule slugs are not listed', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).not.toContainText(
        'keep-operations-small-focused',
      );
    });
  });

  scenario('opening the rules child lists those rules', ({ given, when, then }) => {
    given('a Node with applicable rules', async () => {
      await openPmlDomain();
      await waitForTree();
      await explorer().getByRole('button', { name: 'Show rules' }).click({ timeout: 5_000 });
      for (let step = 0; step < 40; step += 1) {
        if (await explorer().getByTestId('tree-expand-rules').count()) {
          break;
        }
        const closed = explorer().locator('[data-testid="tree-expand"][aria-expanded="false"]');
        if ((await closed.count()) === 0) {
          break;
        }
        await closed.first().click();
      }
    });
    when('the Engineer opens the rules child', async () => {
      const rulesTwist = explorer().getByTestId('tree-expand-rules').first();
      await expect(rulesTwist).toBeVisible({ timeout: 10_000 });
      await rulesTwist.click();
    });
    then('those rules are listed', async () => {
      await expect(explorer().getByTestId('practice-graph-tree').locator('.rule-status').first()).toBeVisible();
    });
  });
});
