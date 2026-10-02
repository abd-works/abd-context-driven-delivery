import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Filter Graph', () => {
  scenario('each filter panel has its action buttons', ({ given, when, then }) => {
    given('pml-domain is loaded into the KnowledgeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer looks at the filter strip', async () => {});
    then('the practice filter has action buttons', async () => {
      await expect(explorer().getByTestId('filter-practice').locator('..').locator('.filter-actions button').first()).toBeVisible();
    }).and('the node filter has action buttons', async () => {
      await expect(explorer().getByTestId('filter-node').locator('..').locator('.filter-actions button').first()).toBeVisible();
    });
  });

  scenario('selecting a practice narrows the next filter', ({ given, when, then }) => {
    given('pml-domain is loaded into the KnowledgeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer selects the stories practice', async () => {
      await explorer().getByTestId('filter-practice').selectOption('stories');
    });
    then('the node filter lists Story', async () => {
      await expect(explorer().getByTestId('filter-node').locator('option', { hasText: /^Story$/ })).toHaveCount(1);
    }).and('the node filter drops Module', async () => {
      await expect(explorer().getByTestId('filter-node').locator('option', { hasText: 'Module' })).toHaveCount(0);
    });
  });

  scenario('tree lists only Nodes that match the filters', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await openPmlDomain();
      await waitForTree();
    }).and('whose source includes a Node that fails keep-operations-small-focused', async () => {});
    when('the Engineer filters the KnowledgeGraph using violations', async () => {
      await explorer().getByRole('button', { name: /^violations$/i }).click({ timeout: 5_000 });
    }).and('using keep-operations-small-focused', async () => {
      await explorer().getByTestId('filter-rule').selectOption('keep-operations-small-focused');
    });
    then('the failing Node is listed', async () => {
      await expect(explorer().locator('.tree-violating').first()).toBeVisible();
    }).and('the passing Node is not listed', async () => {
      await expect(explorer().locator('.rule-status.passing')).toHaveCount(0);
    });
  });
});
