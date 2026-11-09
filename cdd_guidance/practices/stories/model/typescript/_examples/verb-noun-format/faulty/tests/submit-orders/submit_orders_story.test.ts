import { scenario, story } from "stories/story-test";

story('CartStuff', () => {
  scenario('a customer submits an order', ({ given }) => {
    given('a customer has a basket', () => {
      basket.fill();
    });
  });
});
