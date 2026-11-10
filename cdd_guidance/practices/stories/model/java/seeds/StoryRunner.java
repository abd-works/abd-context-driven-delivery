// StoryRunner.java — generic runner for JUnit tier tests.
//
// Tier test classes hand this runner a Scenario and a factory that produces
// their `TierImpl`; the runner walks `given`, `when`, then produces one JUnit
// dynamic test per `then` step so each observable outcome is a separate row.

package stories;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.TestFactory;

import static org.junit.jupiter.api.DynamicTest.dynamicTest;

public final class StoryRunner {
    private StoryRunner() {}

    private static void dispatch(String step, Map<String, Runnable> table, String phase) {
        Runnable fn = table.get(step);
        if (fn == null) {
            throw new IllegalStateException(
                "Tier is missing a '" + phase + "' implementation for step \"" + step + "\". "
                + "Add it to tier." + phase + "()[\"" + step + "\"]."
            );
        }
        fn.run();
    }

    /**
     * Emit a dynamic test container for one scenario. Bind the returned
     * `List<DynamicTest>` to a `@TestFactory` method in the tier test class.
     */
    public static List<DynamicTest> runScenario(
        String storyName,
        StoryTypes.Scenario scenario,
        Supplier<StoryTypes.TierImpl> makeTier
    ) {
        List<DynamicTest> tests = new ArrayList<>();
        StoryTypes.TierImpl tier = makeTier.get();

        for (String s : scenario.given()) dispatch(s, tier.given(), "given");
        for (StoryTypes.Interaction interaction : scenario.interactions()) {
            for (String s : interaction.when()) dispatch(s, tier.when(), "when");
        }

        int i = 0;
        for (StoryTypes.Interaction interaction : scenario.interactions()) {
            int j = 0;
            for (String s : interaction.then()) {
                final String step = s;
                final String label = (i == 0 && j == 0) ? ("Then " + s) : s;
                tests.add(dynamicTest(label, () -> dispatch(step, tier.then(), "then")));
                j++;
            }
            i++;
        }

        tests.add(dynamicTest("cleanup", tier::cleanup));
        return tests;
    }
}
