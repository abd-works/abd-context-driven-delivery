/** Tier: server - {StoryVerbNoun}Helper backed by the real HTTP route + test DB. */
public class {StoryVerbNoun}StoryTestHelperServer implements {StoryVerbNoun}Helper {
  @Override public void givenPrecondition() throws Exception {
    throw new UnsupportedOperationException("not implemented: givenPrecondition");
  }

  @Override public void whenAction() throws Exception {
    throw new UnsupportedOperationException("not implemented: whenAction");
  }

  @Override public void thenOutcome() throws Exception {
    throw new UnsupportedOperationException("not implemented: thenOutcome");
  }

  @org.junit.jupiter.api.Test
  void runStory() throws Exception {
    {StoryVerbNoun}Story.create(this);
  }
}
