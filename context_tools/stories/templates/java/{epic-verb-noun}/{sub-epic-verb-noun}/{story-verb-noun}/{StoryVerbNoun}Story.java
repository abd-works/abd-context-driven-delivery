/**
 * Story: {Story Verb-Noun} (scenario fidelity - tier-neutral).
 * Calls helper-interface methods only - no assertions, no tier mechanism here.
 *
 * Tiers: {StoryVerbNoun}TestHelper{Tier}.java implements {StoryVerbNoun}Helper
 * (Tier in Domain | Client | Server | E2e | project-specific, e.g. Api, Db).
 * Java file-name-matches-class-name rule concatenates the tier PascalCase
 * onto the class name rather than using a dot suffix.
 */
interface {StoryVerbNoun}Helper {
  void givenPrecondition() throws Exception;
  void whenAction() throws Exception;
  void thenOutcome() throws Exception;
}

public final class {StoryVerbNoun}Story {
  private {StoryVerbNoun}Story() {}

  public static void create({StoryVerbNoun}Helper h) throws Exception {
    mainFlow(h);
  }

  private static void mainFlow({StoryVerbNoun}Helper h) throws Exception {
    h.givenPrecondition();
    h.whenAction();
    h.thenOutcome();
  }
}
