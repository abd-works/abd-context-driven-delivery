import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, expandClosedNodes, expandClosedRules, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Browse Practice Graphs', () => {
  scenario('KnowledgeGraph lists PracticeGraphs and Nodes', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await openPmlDomain();
      await waitForTree();
    }).and('whose source includes a Node that fails keep-operations-small-focused', async () => {});
    when('the Engineer browses the KnowledgeGraph', async () => {
      await explorer().getByRole('button', { name: 'Show rules' }).click({ timeout: 5_000 });
      await expandClosedNodes();
      await expandClosedRules();
    });
    then('the passing Node lists keep-operations-small-focused as passing', async () => {
      await expect(explorer().locator('.rule-status.passing', { hasText: 'keep-operations-small-focused' })).toBeVisible();
    }).and('the failing Node lists keep-operations-small-focused as violating', async () => {
      await expect(explorer().locator('.rule-status.violating', { hasText: 'keep-operations-small-focused' })).toBeVisible();
    }).and('lists a Story', async () => {
      await expect(explorer().locator('button[title="Story"]')).toBeVisible();
    });
  });

  scenario('a Story lists its background, scenarios, steps, and examples', ({ given, when, then }) => {
    given('pml-domain stories are loaded', async () => {
      await openPmlDomain();
      await waitForTree('Stories');
    });
    when('the Engineer opens Select Plan (Onboarding)', async () => {
      await expand('Stories');
      await expand('tests');
      await expand('onboard-a-customer');
      await expand('Onboard A Customer');
      await expand('Select Plan (Onboarding)');
      await expand('Background');
      await explorer().getByRole('button', { name: 'Select Plan (Onboarding)', exact: true }).first().click();
    });
    then('the Story lists a Background, a Scenario, a Step, and an Example', async () => {
      const storyNode = explorer().locator('li[data-kind="Story"]').filter({
        has: explorer().getByRole('button', { name: 'Select Plan (Onboarding)', exact: true }),
      }).first();
      await expect(storyNode.locator('li[data-kind="Background"]').first()).toBeVisible();
      await expect(storyNode.getByRole('button', { name: 'Prospect selects a plan after email verification', exact: true }).first()).toBeVisible();
      await expect(storyNode.getByRole('button', { name: 'Given the plan catalog contains purchasable plans', exact: true }).first()).toBeVisible();
      await expect(storyNode.getByRole('button', { name: 'inventoryMsisdnExamples', exact: true }).first()).toBeVisible();
    }).and('the panel shows the story source', async () => {
      await expect(explorer().locator('.source-path')).toContainText('select-plan-onboarding.e2e.ts');
      await expect(explorer().getByTestId('source-excerpt')).toContainText("story('Select Plan (Onboarding)'", { timeout: 30_000 });
    });
  });
});
