import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Show Disk Packages', () => {
  scenario('disk folders show under a Module', ({ given, when, then }) => {
    given('pml-domain has a domain folder on disk', async () => {
      await openPmlDomain();
    });
    when('the Engineer browses the KnowledgeGraph', async () => {
      await waitForTree();
    });
    then('domain is listed', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText('domain');
    }).and('customer is listed under it', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText('customer');
    });
  });
});
