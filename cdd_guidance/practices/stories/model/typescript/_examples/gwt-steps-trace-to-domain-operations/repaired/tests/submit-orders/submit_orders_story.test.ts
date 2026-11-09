import { scenario, story } from "stories/story-test";

class Cart {}

story('Submit Order', () => {
  scenario('a customer submits an order', ({ given }) => {
    given('a Cart exists', () => {
      basket.fill();
    });
  });
});
