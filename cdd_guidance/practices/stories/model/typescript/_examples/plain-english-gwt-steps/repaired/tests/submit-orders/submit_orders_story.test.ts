import { scenario, story } from "stories/story-test";

story('Submit Order', () => {
  scenario('a customer submits an order', ({ given }) => {
    given('a Customer exists', () => {
      basket.fill();
    });
  });
});
