import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Browse Practice Graphs', () => {
  scenario('KnowledgeGraph lists PracticeGraphs and Nodes', ({ given, when, then }) => {
    given('pml-domain has been selected as the working folder', async () => {
      await openPmlDomain();
    });
    when('the Engineer browses the KnowledgeGraph', async () => {
      await waitForTree();
    });
    then('the tree lists domain', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText('domain');
    }).and('lists customer', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText('customer');
    }).and('lists Customer', async () => {
      await expect(explorer().getByTestId('practice-graph-tree')).toContainText('Customer');
    });
  });
});
