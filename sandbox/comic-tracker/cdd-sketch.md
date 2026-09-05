isual Metaphor & Layout

Implement an interactive subway-map visualization where comic series are rendered as unbroken lines and individual issues are rendered as "stops."
Draw transfer connections between series for cross-series continuations and event reading orders.
Implement a horizontal "era ruler" for the x-axis, using publication dates for positioning but not for deriving sequence.
Use a "hide-not-dim" rendering logic: stops and line segments that are filtered out should not be drawn at all, rather than rendered at lower opacity.
Data & Identity

Load all data from an external, hard-numbered JSON fixture (no inference of reading order or topology).
Define series identity by title and volume/year (e.g., Spider-Man (1963) vs. Spider-Man (2003)).
Support Team protagonists with time-varying memberships (start/end issue spans).
Support character tagging at both the series and issue levels for guest appearances and membership tracking.
Search & Selection

Build a unified search box that matches against Series, Events, and Issues (one-off appearances).
Implement two distinct rosters: an Active Series Roster and an Active Event Roster.
Support drag-and-drop for adding series from search results to the active roster.
Enable click-to-add functionality for Series, Events, and Issues.
Filtering & Visibility

Implement visibility toggles for each entry in the series and event rosters.
Support character-based filtering: when a team-protagonist series is matched via a character search, show only the line segments where that character was an active member.
Support issue-set filtering: when specific issues are added, render the series lane but only show the specific "guest" stops.
Implement a global era filter to narrow the time window of the map.
Navigation & Interaction

Implement a "Stop Hover Card" showing issue details (synopsis, characters, event memberships).
Implement a pinned "Issue Detail Panel" with navigation controls:
Next: Smart navigation prioritizing the current active event, then explicit continuations, then default series order.
Next in Series: Linear walk through the current volume.
Continues In: Explicit jump to a target issue (often on a different line).
Handle multi-event ambiguity: if an issue belongs to multiple events, prompt the user to select the active reading context.
Add deep-linking to the Marvel Unlimited iOS app (marvelunlimited://reader/{id}) when a digital ID is present in the data.
Styling

Apply series-specific colors to series lines and neutral colors to general continuation transfers.
Apply event-specific colors to transfers belonging to a specific storyline.
Ensure all lines and transfers use consistent weight and solid styling.


Agent
Gemini 3 Flash
