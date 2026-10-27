function story(name, fn) { fn() }
function scenario(name, fn) { fn() }
function given(name, fn) { fn() }
function when(name, fn) { fn() }
function then(name, fn) { fn() }

class Cart {}

story("CartStuff", () => {
  scenario("happy", () => {
    given("validPayload", () => {});
    when("the system runs", () => {});
    then("ok", () => {});
  });
});

story("Handle Request", () => {
  scenario("happy", () => {
    given("a Cart exists", () => {});
    when("the Cart adds", () => {});
    then("the Cart is stored", () => {});
  });
});
