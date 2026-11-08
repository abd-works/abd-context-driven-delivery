import { scenario, story } from "stories/story-test";
import { validCustomer } from "./examples/customers.examples";

// examples: validCustomer

story('Onboard Customer', () => {
  scenario('a customer signs up', ({ given }) => {
    given('a customer signs up with an email', () => {
      signUp(validCustomer);
    });
  });
});
