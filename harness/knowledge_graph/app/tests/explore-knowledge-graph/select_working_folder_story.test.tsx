import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { PML_DOMAIN, bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Select Working Folder', () => {
  scenario('selecting a folder scans it into the KnowledgeGraph', ({ given, when, then }) => {
    given('pml-domain is a repo folder', async () => {});
    when('the Engineer selects that folder', async () => {
      await openPmlDomain();
    });
    then('the chosen folder is pml-domain', async () => {
      await expect(explorer().getByTestId('chosen-folder')).toHaveValue(PML_DOMAIN);
    }).and('the PracticeGraph lists domain', async () => {
      await waitForTree();
    });
  });
});
