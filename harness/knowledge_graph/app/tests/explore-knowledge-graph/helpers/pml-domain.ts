import { expect, test, type Page } from '@playwright/test';

export const PML_DOMAIN =
  'C:\\Users\\jeffa\\OneDrive - abd.works\\personal\\paradise-mobile\\pml-domain';

let page: Page;

export function bindPage(): void {
  test.beforeEach(async ({ page: next }) => {
    page = next;
  });
}

export function explorer(): Page {
  return page;
}

export async function openPmlDomain(): Promise<void> {
  await page.addInitScript((folder: string) => {
    window.localStorage.setItem('kg-scan-root-v2', folder);
    window.localStorage.removeItem('kg-scan-graph-id-v2');
  }, PML_DOMAIN);
  await page.goto('/');
  const chosen = page.getByTestId('chosen-folder');
  await expect(chosen).toBeVisible({ timeout: 30_000 });
  await chosen.fill(PML_DOMAIN);
  await chosen.press('Enter');
}

export async function waitForTree(): Promise<void> {
  await expect(page.getByTestId('practice-graph-tree')).toContainText('domain', {
    timeout: 180_000,
  });
}

export async function waitForWork(action: string): Promise<void> {
  await expect(page.getByTestId('work-progress')).toContainText(`${action} done`, {
    timeout: 15 * 60 * 1000,
  });
}
