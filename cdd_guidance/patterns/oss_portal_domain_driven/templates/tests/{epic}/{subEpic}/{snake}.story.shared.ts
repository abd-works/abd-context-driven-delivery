// States each story once; the domain, service, and BFF specs run it.
import { shareStory } from 'test-utils/story-test/story-test';

export const {{Screen}}Story = shareStory('{{Screen}}', ({ scenario }) => {
  scenario('A draft application is submitted', ({ given, when, then }) => {
    given('a draft application', ({ repositories }) => repositories.{{aggregate}}.create(draftApplication));
    when('the applicant submits it', ({ tier }) => tier.submit(draftApplication.id));
    then('it is submitted', async ({ repositories, expect }) => {
      expect((await repositories.{{aggregate}}.load(draftApplication.id))?.status).toBe('submitted');
    });
  });
});
