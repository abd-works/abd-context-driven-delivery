const page = { getByTestId(id: string) { return id; } };
function expect(value: unknown) {
  return { toHaveText(text: string) { return { value, text }; } };
}
function then(body: () => void) { body(); }
then(() => {
  expect(page.getByTestId("send-wire-destination")).toHaveText("/wires/send");
});
