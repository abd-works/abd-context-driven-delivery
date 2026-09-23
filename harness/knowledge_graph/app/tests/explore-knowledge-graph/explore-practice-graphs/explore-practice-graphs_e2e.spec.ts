import { test, expect, type Page } from '@playwright/test';
import { ExplorePracticeGraphsE2eHelper } from './helpers/explore-practice-graphs.e2e';
import { FIXTURE_WORKSPACE, KEEP_OPERATIONS_SMALL_FOCUSED } from './helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsE2eHelper();

async function expandTree(page: Page) {
  for (let step = 0; step < 20; step += 1) {
    const closed = page.locator('[data-testid="tree-expand"][aria-expanded="false"]');
    if ((await closed.count()) === 0) {
      break;
    }
    await closed.first().click();
  }
  for (let step = 0; step < 20; step += 1) {
    const closed = page.locator('[data-testid="tree-expand-rules"][aria-expanded="false"]');
    if ((await closed.count()) === 0) {
      return;
    }
    await closed.first().click();
  }
}

test('Select Working Folder scans the folder into the tree', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('working-folder').setInputFiles(FIXTURE_WORKSPACE);
  await expandTree(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText('load');
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
});

test('Browse Practice Graphs shows passing and violating rules', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await expandTree(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText('load');
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
});

test('PracticeGraph tree indents children under their parents', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await expandTree(page);
  const parent = page.locator('[data-testid="practice-graph-tree"] li[data-depth="0"] > .tree-row').first();
  const child = page.locator('[data-testid="practice-graph-tree"] li[data-depth="1"] > .tree-row').first();
  const parentBox = await parent.boundingBox();
  const childBox = await child.boundingBox();
  expect(parentBox).toBeTruthy();
  expect(childBox).toBeTruthy();
  expect(childBox!.x).toBeGreaterThan(parentBox!.x);
});
