import { expect } from '@playwright/test';
import { story, scenario } from '../story-test';
import { bindPage, explorer, openPmlDomain, waitForTree } from './helpers/pml-domain';

bindPage();

story('Indent Practice Graph', () => {
  scenario('children sit one indent level under their parent', ({ given, when, then }) => {
    given('a KnowledgeGraph with a parent Node and a child Node', async () => {
      await openPmlDomain();
    });
    when('the Engineer browses the KnowledgeGraph', async () => {
      await waitForTree();
    });
    then('the child sits one indent level under the parent', async () => {
      const parent = explorer().locator('li[data-depth="0"]').first();
      const child = parent.locator('li[data-depth="1"]').first();
      await expect(child).toBeVisible();
      const parentBox = await parent.locator('.node-name').first().boundingBox();
      const childBox = await child.locator('.node-name').first().boundingBox();
      expect(childBox!.x).toBeGreaterThan((parentBox?.x ?? 0) + 8);
    });
  });
});
