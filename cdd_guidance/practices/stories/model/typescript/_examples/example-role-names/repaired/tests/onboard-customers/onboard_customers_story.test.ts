import { scenario, story } from "stories/story-test";

// examples: enteredCustomer
export const enteredCustomer = { email: 'ann@example.com' };

story('Onboard Customer', () => {
  scenario('a customer signs up', ({ given }) => {
    given('a customer signs up with an email', () => {
      signUp(enteredCustomer);
    });
  });
});
