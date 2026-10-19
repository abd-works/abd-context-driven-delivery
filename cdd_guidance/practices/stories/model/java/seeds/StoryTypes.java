// StoryTypes.java — shared types for every generated tests package.
//
// Java's type system can enforce the general shape but not the exact keyset
// of a `Map<String, Runnable>` at compile time — the runner uses runtime
// step-key assertions, matching the Python and JavaScript runners.

package stories;

import java.util.List;
import java.util.Map;

public final class StoryTypes {
    private StoryTypes() {}

    /** A when-then block within a scenario. */
    public record Interaction(List<String> when, List<String> then) {}

    /** A behaviour walk-through under a story. */
    public record Scenario(String name, List<String> given, List<Interaction> interactions) {}

    /** Story metadata plus a keyed set of scenarios. */
    public interface Story {
        String story();
        String actor();
        List<String> domainTerms();
        List<String> evidence();
        Map<String, Scenario> scenarios();
    }

    /**
     * Tier contract. `given` / `when` / `then` are keyed by the EXACT step
     * strings from the scenario; the runner throws with the missing string
     * and phase when a key is unmapped.
     */
    public interface TierImpl {
        Map<String, Runnable> given();
        Map<String, Runnable> when();
        Map<String, Runnable> then();
        void cleanup();
    }
}
