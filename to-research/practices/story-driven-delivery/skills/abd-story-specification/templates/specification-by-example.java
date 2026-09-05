// <SlugPascalCase>Stories.java
//
// Source of truth for stories in this sub-epic.
// Each static inner class is one story. Test classes import from here.
//
// Structure mirrors the TypeScript format:
//   story             — display name
//   actor             — primary actor
//   acceptance_criteria — list of step-object arrays (when/then/and/but)
//   domain_terms      — key domain concepts
//   evidence          — source files / research
//   named scenario objects — one per AC, containing a steps list

public final class <SlugPascalCase>Stories {

  // ===========================================================================
  // STORY: <Story Display Name>  (plain scenario)
  // ===========================================================================

  public static final class STORY_EXPORT_NAME {
    public static final String story = "<Story Display Name>";
    public static final String actor = "<Actor Name>";

    public static final Object[][] acceptance_criteria = {
      {
        Map.of("when", "the *<actor>* <triggering condition>"),
        Map.of("then", "the **<term>** <observable outcome>"),
        Map.of("and",  "<additional observable outcome>"),
      },
      {
        Map.of("when", "the *<actor>* <alternate condition>"),
        Map.of("then", "<negative outcome>"),
        Map.of("but",  "<state that does NOT change>"),
      },
    };

    public static final String[] domain_terms = { "<term 1>", "<term 2>" };
    public static final String[] evidence     = { "<source file>", "<research doc>" };

    // Scenario for AC[0] — happy path
    public static final Object methodNamedScenarioKey = Map.of(
      "name", "<scenario name in plain words>",
      "steps", List.of(
        Map.of("given", "<precondition>"),
        Map.of("when",  "<action>"),
        Map.of("then",  "<observable outcome 1>"),
        Map.of("and",   "<observable outcome 2>")
      )
    );

    // Scenario for AC[1] — negative path
    public static final Object negativeScenarioKey = Map.of(
      "name", "<negative scenario name>",
      "steps", List.of(
        Map.of("given", "<alternate precondition>"),
        Map.of("when",  "<alternate action>"),
        Map.of("then",  "<negative outcome>"),
        Map.of("but",   "<state that does NOT change>")
      )
    );
  }

  // ===========================================================================
  // STORY: <Second Story Display Name>  (scenario outline — data-driven)
  // ===========================================================================

  public static final List<Map<String, Object>> SECOND_STORY_EXAMPLES = List.of(
    Map.of("scenario", "Scenario 1", "param_a", "<value>", "param_b", true,  "expected_result", "<outcome 1>"),
    Map.of("scenario", "Scenario 2", "param_a", "<value>", "param_b", false, "expected_result", "<outcome 2>")
  );

  public static final class SECOND_STORY_EXPORT_NAME {
    public static final String story = "<Second Story Display Name>";
    public static final String actor = "<Actor Name>";

    public static final Object[][] acceptance_criteria = {
      {
        Map.of("when", "the *<actor>* sets {param_a}"),
        Map.of("then", "result is {expected_result}"),
      },
    };

    public static final String[] domain_terms = { "<term>" };
    public static final String[] evidence     = { "<source>" };

    public static final Object outlineScenarioKey = Map.of(
      "name",     "<scenario outline name>",
      "examples", SECOND_STORY_EXAMPLES,
      "steps", List.of(
        Map.of("given", "<shared Given from BACKGROUND or explicit here>"),
        Map.of("when",  "<action with {param_a}>"),
        Map.of("then",  "result: {expected_result}")
      )
    );
  }
}
