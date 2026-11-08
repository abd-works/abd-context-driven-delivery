import { scenario, story } from "stories/story-test";
import { enteredCustomer } from "./examples/customers.examples";

// examples: enteredCustomer

story('Onboard Customer', () => {
  scenario('a customer signs up', ({ given }) => {
    given('a customer signs up with an email', () => {
      signUp(enteredCustomer);
    });
  });
});
