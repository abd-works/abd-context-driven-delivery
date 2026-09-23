import { test, expect } from '@playwright/test';
import { ExplorePracticeGraphsE2eHelper } from './helpers/explore-practice-graphs.e2e';
import { FIXTURE_WORKSPACE, KEEP_OPERATIONS_SMALL_FOCUSED } from './helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsE2eHelper();

test('Select Working Folder scans the folder into the tree', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('working-folder').setInputFiles(FIXTURE_WORKSPACE);
  await expect(page.getByTestId('practice-graph-tree')).toContainText('load');
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
});

test('Browse Practice Graphs shows passing and violating rules', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await expect(page.getByTestId('practice-graph-tree')).toContainText('load');
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
});
