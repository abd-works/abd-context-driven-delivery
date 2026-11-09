import { scenario, story } from "stories/story-test";

story('Submit Order', () => {
  scenario('a customer submits an order', ({ given }) => {
    given('validPayload', () => {
      basket.fill();
    });
  });
});
