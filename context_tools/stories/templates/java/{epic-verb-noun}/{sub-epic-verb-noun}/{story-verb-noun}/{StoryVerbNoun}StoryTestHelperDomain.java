/** Tier: domain - {StoryVerbNoun}Helper backed by direct domain-class calls. */
public class {StoryVerbNoun}StoryTestHelperDomain implements {StoryVerbNoun}Helper {
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
