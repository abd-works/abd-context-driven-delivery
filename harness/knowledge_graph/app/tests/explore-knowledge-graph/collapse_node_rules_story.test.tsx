import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Collapse Node Rules', () => {
  scenario('rules stay collapsed until the Node is expanded', ({ given, when, then }) => {
    given('a Node with applicable rules', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer expands that Node without opening rules', async () => {
      await explorer().getByRole('button', { name: /^Expand / }).first().click();
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
    });
    when('the Engineer opens the rules child', async () => {
      await explorer().getByTestId('tree-expand-rules').first().click();
    });
    then('those rules are listed', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText(
        'keep-operations-small-focused',
      );
    });
  });
});
