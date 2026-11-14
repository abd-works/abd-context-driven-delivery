test('apply for camp', async ({ page }) => {
  await page.goto('/summer-camp/apply');
  await page.getByRole('button', { name: 'Submit' }).click();
});
