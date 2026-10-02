import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, expand, explorer, openFolder, openPmlDomain, RULE_OUTCOMES, waitForTree } from './helpers/pml-domain';

bindPage();

story('Open Node Source', () => {
  scenario('file Node opens source and highlights range', ({ given, when, then }) => {
    given('a KnowledgeGraph with a file Node that has a source file and range', async () => {
      await openFolder(RULE_OUTCOMES);
      await waitForTree('Clean Engineering');
    });
    when('the Engineer selects the file Node', async () => {
      await expand('Clean Engineering');
      await expand('orders');
      await expand('Order');
      await explorer().getByRole('button', { name: 'processEverything', exact: true }).click({ timeout: 15_000 });
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
      await waitForTree('Clean Engineering');
    });
    when('the Engineer selects the operation Node', async () => {
      await explorer().getByRole('button', { name: 'Show rules' }).click({ timeout: 5_000 });
      await explorer().getByRole('button', { name: 'processEverything', exact: true }).click({ timeout: 15_000 });
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

  scenario('a scenario pane shows the whole scenario', ({ given, when, then }) => {
    given('pml-domain stories are loaded', async () => {
      await openPmlDomain();
      await waitForTree('Stories');
    });
    when('the Engineer selects Customer submits feedback', async () => {
      await expand('Stories');
      await expand('tests');
      await expand('access-selfcare');
      await expand('Access Selfcare');
      await expand('Access Selfcare');
      await expand('Get Support');
      await explorer().getByRole('button', { name: /Customer submits feedback/ }).first().click({ timeout: 15_000 });
    });
    then('the pane shows the scenario and everything inside it', async () => {
      const body = explorer().getByTestId('source-excerpt');
      await expect(body).toContainText("scenario('Customer submits feedback'", { timeout: 30_000 });
      await expect(body).toContainText('they send a feedback note');
      await expect(body).toContainText('thanks for your feedback is shown');
      await expect(body).toContainText('the receipt is for this customer');
    }).and('the step lists each example and the operation it calls', async () => {
      await expand('When they send a feedback note');
      const step = explorer().locator('li[data-kind="Step"]').filter({ hasText: 'When they send a feedback note' }).first();
      await expect(step.getByRole('button', { name: 'Example feedbackSubjectExample' })).toBeVisible();
      await expect(step.getByRole('button', { name: 'Example feedbackMessageExample' })).toBeVisible();
      await expect(step.getByRole('button', { name: 'Operation submitFeedback' })).toBeVisible();
      await step.getByRole('button', { name: 'Step When they send a feedback note' }).click();
      await expect(explorer().locator('.call-fold').first()).toBeVisible({ timeout: 20_000 });
    });
  });

  scenario('an epic pane shows every story inside it', ({ given, when, then }) => {
    given('pml-domain stories are loaded', async () => {
      await openPmlDomain();
      await waitForTree('Stories');
    });
    when('the Engineer selects Access Selfcare', async () => {
      await expand('Stories');
      await expand('tests');
      await expand('access-selfcare');
      await explorer().getByRole('button', { name: 'Access Selfcare', exact: true }).first().click();
    });
    then('the pane shows the stories in that epic', async () => {
      const body = explorer().getByTestId('source-excerpt');
      await expect(body).toContainText("story('Get Support'", { timeout: 30_000 });
      await expect(body).toContainText("story('Sign In'");
    });
  });
});
