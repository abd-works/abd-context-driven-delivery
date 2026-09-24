import { test, expect, type Page } from '@playwright/test';
import { ExplorePracticeGraphsE2eHelper } from './helpers/explore-practice-graphs.e2e';
import {
  FIXTURE_WORKSPACE,
  KEEP_OPERATIONS_SMALL_FOCUSED,
} from './helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsE2eHelper();

async function expandNodes(page: Page) {
  for (let step = 0; step < 20; step += 1) {
    const closed = page.locator(
      '[data-testid="tree-expand"][aria-expanded="false"]',
    );
    if ((await closed.count()) === 0) {
      return;
    }
    await closed.first().click();
  }
}

async function expandRules(page: Page) {
  for (let step = 0; step < 20; step += 1) {
    const closed = page.locator(
      '[data-testid="tree-expand-rules"][aria-expanded="false"]',
    );
    if ((await closed.count()) === 0) {
      return;
    }
    await closed.first().click();
  }
}

async function waitForTree(page: Page) {
  await expect(page.getByTestId('practice-graph-tree')).toContainText('domain', {
    timeout: 15000,
  });
  await expandNodes(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText('load');
}

test.beforeEach(async ({ page, request }) => {
  await page.addInitScript(() => {
    window.localStorage.removeItem('kg-scan-graph-id');
    window.localStorage.removeItem('kg-scan-root');
    window.localStorage.removeItem('kg-scan-graph-id-v2');
    window.localStorage.removeItem('kg-scan-root-v2');
  });
  await helper.seed(request);
});

test('Select Working Folder scans the folder into the tree', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    'Select a repo folder to load the Knowledge Graph.',
  );
  await page.getByTestId('working-folder').setInputFiles(FIXTURE_WORKSPACE);
  await waitForTree(page);
  await expandRules(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
});

test('Browse Practice Graphs shows passing and violating rules', async ({
  page,
}) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  await expandRules(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
});

test('PracticeGraph tree indents children under their parents', async ({
  page,
}) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  const parent = page
    .locator('[data-testid="practice-graph-tree"] li[data-depth="0"] > .tree-row')
    .first();
  const child = page
    .locator('[data-testid="practice-graph-tree"] li[data-depth="1"] > .tree-row')
    .first();
  const parentBox = await parent.boundingBox();
  const childBox = await child.boundingBox();
  expect(parentBox).toBeTruthy();
  expect(childBox).toBeTruthy();
  expect(childBox!.x).toBeGreaterThan(parentBox!.x);
});

test('hover names the Node type', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  await expect(
    page.locator('[data-kind="Package"] title').first(),
  ).toHaveText('Package');
  await expect(
    page.locator('[data-kind="Class"] title').first(),
  ).toHaveText('Class');
});

test('classes sit in their subfolder', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  const customerFolder = page
    .locator('[data-testid="practice-graph-tree"] li')
    .filter({ has: page.locator('.tree-name', { hasText: /^customer$/ }) })
    .first();
  await expect(customerFolder).toContainText('Customer');
});

test('disk folders show under a Module', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText('domain');
  await expect(page.getByTestId('practice-graph-tree')).toContainText('customer');
});

test('rules stay collapsed until the rules Node is opened', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  await expect(page.getByTestId('practice-graph-tree')).not.toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
  await expandRules(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    KEEP_OPERATIONS_SMALL_FOCUSED,
  );
});

test('file Node opens source', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  await page.locator('.tree-name', { hasText: /^load$/ }).click();
  await expect(page.getByTestId('source-file')).toContainText('load');
  await expect(page.locator('.monaco-editor').first()).toBeVisible();
});

test('following a Node focuses its source', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  await page.locator('.tree-name', { hasText: /^processEverything$/ }).click();
  await expect(page.getByTestId('source-file')).toContainText('processEverything');
  await expect(page.locator('.monaco-editor').first()).toBeVisible();
});

test('violations filter keeps the failing Node', async ({ page }) => {
  await page.goto(helper.graphQuery());
  await waitForTree(page);
  await page.getByLabel('violations').check();
  await expandNodes(page);
  await expect(page.getByTestId('practice-graph-tree')).toContainText(
    'processEverything',
  );
  await expect(page.getByTestId('practice-graph-tree')).not.toContainText('load');
});
