import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Filter Graph', () => {
  scenario('filters sit in the top strip', ({ given, when, then }) => {
    given('pml-domain is loaded into the KnowledgeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer looks at the filters', async () => {});
    then('the practice filter is visible', async () => {
      await expect(explorer().getByTestId('filter-practice')).toBeVisible();
    }).and('the node filter is visible', async () => {
      await expect(explorer().getByTestId('filter-node')).toBeVisible();
    }).and('the PracticeGraph is still listed', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText('domain');
    });
  });
});
