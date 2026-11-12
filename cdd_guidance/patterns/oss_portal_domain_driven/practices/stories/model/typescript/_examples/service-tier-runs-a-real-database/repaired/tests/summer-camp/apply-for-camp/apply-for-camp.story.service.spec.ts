beforeAll(() => throwawayDatabase.migrate('summer-camp-service'));
runStory(applyForCamp, repositories.service);
