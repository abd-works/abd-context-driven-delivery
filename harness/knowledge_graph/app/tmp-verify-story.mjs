import { chromium } from '@playwright/test';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto('http://localhost:3000/?folder=PML%20domain');
const chosen = page.getByTestId('chosen-folder');
await chosen.fill('PML domain');
await chosen.press('Enter');
await page.getByTestId('practice-graph-tree').getByText('tests', { exact: true }).first().waitFor({ timeout: 180000 });
await page.getByRole('button', { name: 'Expand onboard-a-customer', exact: true }).first().click();
await page.getByRole('button', { name: 'Expand Select Plan (Onboarding)', exact: true }).first().click();
await page.getByRole('button', { name: 'Expand Background', exact: true }).first().click();
const story = page.locator('li[data-kind="Story"]').filter({
  has: page.getByRole('button', { name: 'Select Plan (Onboarding)', exact: true }),
}).first();
const kids = await story.locator(':scope > ul > li').evaluateAll((rows) =>
  rows.map((row) => `${row.getAttribute('data-kind')}: ${row.querySelector('.node-name')?.textContent ?? ''}`),
);
const steps = await story.locator('li[data-kind="Step"] .node-name').allTextContents();
await page.getByTestId('filter-practice').selectOption(['stories']);
const connectors = await page.getByTestId('filter-connector').locator('option').allTextContents();
const nodes = await page.getByTestId('filter-node').locator('option').allTextContents();
console.log(JSON.stringify({ kids, steps, connectors, nodes }, null, 2));
await browser.close();
