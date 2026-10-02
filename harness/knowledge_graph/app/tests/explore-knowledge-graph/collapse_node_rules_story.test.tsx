import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Collapse Node Rules', () => {
  scenario('rules stay collapsed until the rules Node is opened', ({ given, when, then }) => {
    given('a Node with applicable rules', async () => {
      await openPmlDomain();
    });
    when('the Engineer expands that Node without opening rules', async () => {
      await waitForTree();
    });
    then('rule slugs are not listed', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).not.toContainText(
        'keep-operations-small-focused',
      );
    });
  });
});
