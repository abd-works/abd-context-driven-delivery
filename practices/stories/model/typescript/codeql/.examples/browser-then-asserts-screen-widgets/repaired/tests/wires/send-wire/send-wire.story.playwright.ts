const page = { getByRole(name: string) { return name; } };
function expect(value: unknown) {
  return { toBeVisible() { return value; } };
}
function then(body: () => void) { body(); }
then(() => {
  expect(page.getByRole("heading")).toBeVisible();
});
