import { scenario, story } from "stories/story-test";

// examples: validCustomer
export const validCustomer = { email: 'ann@example.com' };

story('Onboard Customer', () => {
  scenario('a customer signs up', ({ given }) => {
    given('a customer signs up with an email', () => {
      signUp(validCustomer);
    });
  });
});
