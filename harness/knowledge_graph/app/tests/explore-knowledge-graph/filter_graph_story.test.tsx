import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Filter Graph', () => {
  scenario('the Engineer can open filters on the loaded graph', ({ given, when, then }) => {
    given('pml-domain is loaded into the KnowledgeGraph', async () => {
      await openPmlDomain();
      await waitForTree();
    });
    when('the Engineer toggles filters', async () => {
      await explorer().getByTestId('toggle-filters').click();
    });
    then('the PracticeGraph is still listed', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText('domain');
    });
  });
});
