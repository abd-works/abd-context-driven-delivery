import { expect, test, type Page } from '@playwright/test';

export const PML_DOMAIN =
  'C:\\Users\\jeffa\\OneDrive - abd.works\\personal\\paradise-mobile\\pml-domain';

export const RULE_OUTCOMES = 
  'C:\\dev\\abd-context-driven-delivery\\harness\\knowledge_graph\\app\\tests\\explore-knowledge-graph\\fixtures\\rule-outcomes';

let page: Page;

export function bindPage(): void {
  test.beforeEach(async ({ page: next }) => {
    page = next;
  });
}

export function explorer(): Page {
  return page;
}

export async function openFolder(folder: string): Promise<void> {
  await page.addInitScript((root: string) => {
    window.localStorage.setItem('kg-scan-root-v2', root);
    window.localStorage.removeItem('kg-scan-graph-id-v2');
  }, folder);
  await page.goto('/');
  const chosen = page.getByTestId('chosen-folder');
  await expect(chosen).toBeVisible({ timeout: 30_000 });
  await chosen.fill(folder);
  await chosen.press('Enter');
}

export async function openPmlDomain(): Promise<void> {
  await openFolder(PML_DOMAIN);
}

export async function waitForTree(label = 'Clean Engineering'): Promise<void> {
  await expect(page.getByTestId('practice-graph-tree')).toContainText(label, {
    timeout: 180_000,
  });
}

export async function expand(name: string): Promise<void> {
  const button = page.getByRole('button', { name: `Expand ${name}`, exact: true }).first();
  await expect(button).toBeVisible({ timeout: 30_000 });
  await button.click();
}

export async function waitForWork(action: string): Promise<void> {
  await expect(page.getByTestId('work-progress')).toContainText(`${action} done`, {
    timeout: 2 * 60 * 60 * 1000,
  });
}
