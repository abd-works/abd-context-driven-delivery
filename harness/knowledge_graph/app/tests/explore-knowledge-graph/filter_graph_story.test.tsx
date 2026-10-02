import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openFolder, openPmlDomain, RULE_OUTCOMES, waitForTree } from './helpers/pml-domain';

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
    }).and('every filter option starts on', async () => {
      for (const testId of ['filter-practice', 'filter-stage', 'filter-node', 'filter-rule']) {
        await expect.poll(async () =>
          explorer().getByTestId(testId).evaluate((el: HTMLSelectElement) =>
            el.options.length > 0 && el.selectedOptions.length === el.options.length,
          ),
        ).toBe(true);
      }
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
    then('the node filter lists every stories type', async () => {
      await expect(explorer().getByTestId('filter-node').locator('option')).toHaveText([
        'Epic',
        'SubEpic',
        'Story',
        'Background',
        'Scenario',
        'Step',
        'Example',
        'StoryModel',
      ]);
    }).and('the node filter drops Module', async () => {
      await expect(explorer().getByTestId('filter-node').locator('option', { hasText: 'Module' })).toHaveCount(0);
    }).and('the stage filter lists every stories stage', async () => {
      await expect(explorer().getByTestId('filter-stage').locator('option')).toHaveText([
        'discovery',
        'specification',
        'implementation',
      ]);
    }).and('the rule filter lists the stories rules', async () => {
      const rule = explorer().getByTestId('filter-rule');
      await expect(rule.locator('option', { hasText: 'verb-noun-format' })).toHaveCount(1);
      await expect(rule.locator('option', { hasText: 'high-cohesion' })).toHaveCount(0);
      await expect.poll(async () =>
        rule.evaluate((el: HTMLSelectElement) => el.options.length > 0 && el.selectedOptions.length === el.options.length),
      ).toBe(true);
    });
  });

  scenario('selecting clean engineering lists every node type', ({ given, when, then }) => {
    given('pml-domain is loaded into the KnowledgeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer selects the clean engineering practice', async () => {
      await explorer().getByTestId('filter-practice').selectOption('clean_engineering');
    });
    then('the node filter lists every clean engineering type', async () => {
      const node = explorer().getByTestId('filter-node');
      await expect(node.locator('option')).toHaveText([
        'Module',
        'Package',
        'OoadClass',
        'Property',
        'Operation',
        'Parameter',
        'File',
        'CleanEngineeringModel',
      ]);
      await expect.poll(async () =>
        node.evaluate((el: HTMLSelectElement) => el.selectedOptions.length === el.options.length),
      ).toBe(true);
    }).and('the rule filter lists the clean engineering rules', async () => {
      const rule = explorer().getByTestId('filter-rule');
      await expect(rule.locator('option', { hasText: 'high-cohesion' })).toHaveCount(1);
      await expect(rule.locator('option', { hasText: 'keep-operations-small-focused' })).toHaveCount(1);
      await expect(rule.locator('option', { hasText: 'verb-noun-format' })).toHaveCount(0);
      await expect.poll(async () =>
        rule.evaluate((el: HTMLSelectElement) => el.options.length > 10 && el.selectedOptions.length === el.options.length),
      ).toBe(true);
    }).and('Show rules lists high-cohesion on domain', async () => {
      await explorer().getByRole('button', { name: 'Show rules' }).click();
      const domain = explorer().locator('li').filter({
        has: explorer().getByRole('button', { name: 'domain', exact: true }),
      }).first();
      await expect(domain.locator('.rule-status', { hasText: 'high-cohesion' }).first()).toBeVisible();
    }).and('epics and the tests folder are not tagged as clean engineering', async () => {
      const engineering = explorer().locator('li[data-node-id="practice:clean_engineering"]');
      await expect(engineering.locator(':scope > ul > li .node-name', { hasText: /^tests$/ })).toHaveCount(0);
      await expect(engineering.locator('.node-name', { hasText: /^access-selfcare$/ })).toHaveCount(0);
      await expect(engineering.locator('.node-name', { hasText: /^manage-billing$/ })).toHaveCount(0);
      await expect(engineering.locator('.node-name', { hasText: /^manage-services$/ })).toHaveCount(0);
      await expect(engineering.locator('.node-name', { hasText: /^onboard-a-customer$/ })).toHaveCount(0);
      await expect(engineering.getByRole('button', { name: 'Module domain' })).toBeVisible();
    });
  });

  scenario('tree lists only Nodes that match the filters', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await openFolder(RULE_OUTCOMES);
      await waitForTree('orders');
    }).and('whose source includes a Node that fails keep-operations-small-focused', async () => {});
    when('the Engineer filters the KnowledgeGraph using violations', async () => {
      await explorer().getByRole('button', { name: /^violations$/i }).click({ timeout: 5_000 });
      await explorer().getByRole('button', { name: 'Show rules' }).click({ timeout: 5_000 });
    }).and('using keep-operations-small-focused', async () => {
      await explorer().getByTestId('filter-rule').selectOption('keep-operations-small-focused');
    });
    then('the failing Node is listed', async () => {
      await expect(explorer().locator('.tree-violating').first()).toBeVisible();
      await expect(explorer().getByTestId('source-file')).toContainText('processEverything');
      await expect(explorer().getByTestId('source-file')).toContainText('keep-operations-small-focused');
    }).and('the passing Node is not listed', async () => {
      await expect(explorer().locator('.rule-status.passing')).toHaveCount(0);
    });
  });
});
