test('apply for camp', async ({ page }) => {
  await page.route('**/bff/camp-applications', route => route.fulfill({ json: {} }));
  await page.goto('/summer-camp/apply');
});
