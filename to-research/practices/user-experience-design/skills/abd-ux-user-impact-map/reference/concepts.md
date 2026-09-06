# Impact Mapping — Concepts

## What is an impact map?

An impact map is a layered picture of cause and intent, read in a fixed order:

1. **Goal** — Broader organisational outcomes connect to finer-grained outcomes (why). You pick the level you are mapping in detail; actors and behaviour hang off that focus.
2. **Actors** — People, teams, or roles that can help or obstruct (who).
3. **Impacts** — Observable changes in behaviour for each actor (how behaviour should move).
4. **Deliverables** — Hypotheses about what we could build or do to enable those behaviours (what).

It is not a story map, a WBS, or a prioritised backlog by itself. It feeds those artifacts by clarifying how candidate scope links back to outcomes and behaviour. For delivery planning, you can add a phased backlog over named timeboxes (months, quarters, or another convention): each scheduled option still points at one behaviour path on the map so ordering stays tied to outcomes, not to a separate feature list.

### Why use it?

- **Assumptions visible** — Gaps and guesses show on the map instead of hiding in documents.
- **Scope discipline** — Orphan features are obvious when they are not tied to a behaviour you care about.
- **Cross-functional alignment** — Shared picture for product, delivery, and domain voices (when run collaboratively).

---

## Goal

The goal is why you are doing the work: the business outcome the organisation wants — the stakes in play (market, revenue, risk, adoption, compliance, cost, reliability, and similar). Broader outcomes decompose into finer outcomes that roll up to them. The finest-grained outcome on the map is often workshop-sized (about a quarter or less when you timebox).

Phrase each level as an outcome in the world: direction and stakes in language about results (growth, reliability, risk posture, adoption, retention, margin), not shipping labels. Examples: *Grow monthly actives*; *Achieve reliable same-day completion for domestic orders*; *Grow net revenue retention in the enterprise segment*. Put numeric proof on `METRIC:` lines indented under that `GOAL:` (e.g. verified MAU lift), not in the `GOAL:` headline when using this skill's templates. Deliverables hold candidate things to build or ship once behaviour is clear under impacts.

Clear organisational outcomes are specific enough that the team can identify the actors that are necessary to achieving it. Who will help us achieve our outcome?; How should behaviour change?; What could we do to support that impact? Good goals are often nested, starting major (wide intent) narrowing to tactical. They stay customer- and stakeholder-driven toward outcomes in the world. Actors and impacts tie the mapped outcome to who and observable behaviour; deliverables carry what you might ship.

## Goal metrics (`METRIC:` under each `GOAL:`)

Lagging proof tied to outcomes: economic (revenue, margin, unit cost) or strategic (adoption, share, compliance, risk). Attach each at the goal level it measures — numeric bars, percent targets, thresholds, and counts that show the organisation moved.

Example: *Grow monthly actives* with proof on `METRIC:` *verified MAU +20% this quarter vs baseline*; *Achieve reliable same-day completion for domestic orders* with proof *ninety percent same-day*; *Grow net revenue retention in the enterprise segment* with proof *NRR above 110% this fiscal year*.

---

## Actors

An actor is someone who can help or block the outcome in the goal hierarchy: a person, team, or organisation. For each actor, be clear which people or teams you mean and what about their situation matters here (for example new versus returning, channel or market, a lifecycle stage, contract timing, or a stressful moment such as renewal or outage). Words like customer, operator, or partner are fine to start, but you need to make them more specific.

Never cast a product, service, system, or platform as an actor, even when a brief talks that way. Name who actually helps or blocks and put the system under deliverables.

If you only name a vague who ("all customers," "partners," one bucket of "users") but the impacts you list are really about different groups or moments with different behaviour, you are mixing actors. Narrow the situation, name the moment, or split into separate actors so each who matches one coherent narrative.

Every actor on the map should have at least one impact — something you want that actor to do or stop doing. If there is nothing to say about behaviour for that who, merge them with another actor or stop treating them as separate.

---

## Impacts

An impact is the behaviour change you want from a given actor toward those outcomes: what they should start doing, do more of, do less of, or stop doing. It answers *how should this person or team behave differently?* — not *what are we building?* and not *what is the business outcome?* (that lives in the goal hierarchy above).

Good impacts are specific enough to recognise in the world. Someone could watch, read a transcript, pull a metric, or walk a journey and say whether it is happening. They usually lead with a verb the actor performs: completes, submits, shares, invites, triages, opts in, returns, finishes, escalates. In this skill's **shipped hierarchy templates**, keep each `IMPACT:` line to observable behaviour **without** embedded cadence targets, deadlines, SLA timing, or numeric bars — put those on `METRIC:` lines indented under that `IMPACT:` (and in hypotheses after `by` with the impact metric). In live facilitation you may still talk in tighter cadence; when writing the tree, move quotas to metric lines.

One impact is one movement of behaviour. If you mix two behaviours, split them. Do not treat a component, project name, epic title, or system as the impact — that belongs under deliverables (or under engineering planning), not as the behaviour itself. Do not stop at slogans like "better onboarding" with no observable picture.

Contrast: "Submits the order without calling support" describes behaviour; "New checkout microservice" describes a build. "Shares run highlights to social" is an impact headline; weekly share rate belongs on a `METRIC:` line under that impact; "Share sheet v2" is not an impact.

## Impact metrics (`METRIC:` under each `IMPACT:`)

Behaviour and usage proxies (e.g. weekly share rate, D7 retention, hours watched) that should move before goal-level `METRIC:` lines respond. They make each behaviour change testable on its own.

Example: *Shares run highlight to a social channel* with metric *share events per weekly active user*; *Finishes tutorial and first ranked match in the first session* with metrics *D1 ranked-match completion rate*; *Opens abuse report quickly* with metric *median hours to first moderator action*.

---

## Deliverables

Deliverables are candidate things to build, ship, or run that might help produce an impact. They are options and bets — useful for roadmap and prioritisation — not promises and not a substitute for naming behaviour. Phrase them at roadmap granularity: a capability, epic, experiment, or policy change someone could schedule, not a ten-year vision sentence.

Several deliverables under the same impact means different ways you might achieve that one behaviour change. Keep each option one clear idea; split merged features. A deliverable should not restate the goal, duplicate goal metric lines, or copy the impact sentence ("User posts weekly") — those stay where they belong.

Do not hide a grab-bag in one deliverable ("Everything for sharing"); do not use empty words like "Success" as if they were shippable work. If you cannot name a plausible thing to try, you probably need a sharper impact first.

Contrast: under an impact about sharing to social, "One-tap share sheet with clip" and "Seasonal badge asset pack" are deliverables — different bets on the same behaviour. "Grow monthly active players" is goal territory; share rate and cadence sit in metrics, not in the `IMPACT:` headline when using this skill's templates.

---

## Assumptions

An impact map carries two kinds of assumption, and both are already visible in the hypotheses templates:

- **Build assumption** — If we build this deliverable, the target actor will be impacted in a specific way (e.g. their behaviour), measurable by the impact metric. This is a bet on delivery causing behaviour change.
- **Outcome assumption** — If the impact metric moves, the goal metric will follow. This is a bet on the behaviour change mattering to the outcome.

Teams use a validated learning approach to confirm or refute each belief and update the map as they learn — keeping evidence and learning visible. The shared Plan / Validate / Learn loop is defined once in [`../../../reference/validated-learning.md`](../../../reference/validated-learning.md).

The `templates/impact-map-hypotheses.md` (and `.txt`) already phrase both assumption types as testable sentences — they are the natural starting point. Use **abd-simple-validated-learning** to turn those sentences into a prioritised backlog of experiments with owners and explicit failure conditions when the team needs to validate before committing to build.

---

## Phased feature backlog

When delivery needs a time horizon, you extend the same map with a phased backlog: a sequence of timeboxes (months, quarters, or another convention you name once). Each phase holds scheduled options — concrete things you might ship or run. Every option stays tied to exactly one impact path on the map: the same actor and the same behaviour change that option is meant to support. That keeps sequencing honest: order is about *when* you might try something, not a separate story from *why* that something mattered. Orphan work shows up when an option does not link to a behaviour you care about.

---

## The shape of a good impact map

In substance: an outcome hierarchy (broad to the level you are mapping), then for that focus the actors who matter, the observable behaviour you want from each, and the deliverable options that might produce those behaviours. Optional goal metrics sit with the goal level they measure; optional behaviour proxies sit with the impacts (`METRIC:` under each **`IMPACT:`** on the prefix map). A phased backlog, when you need one, orders those deliverable options across timeboxes while preserving the same one-to-one link from each scheduled option to one impact path on the map.
