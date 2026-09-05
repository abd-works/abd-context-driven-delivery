# Impact map — hypotheses (markdown)  

## Instructions (for skill maintainers)  

- Same map as the hierarchy view, as **testable sentences**. Replace every `{{placeholder}}`; remove unused blocks.  
- **Group by goal:** each `### Outcome` section names the **goal** that child hypotheses roll up to (usually the mapped `GOAL:`; add a final section for a **broader** goal if needed).  
- **Outcome sentence:** one **If …, then …** line with the same **actor** and **impact** wording as the tree — **no cadence, deadlines, thresholds, or SLA timing** in the impact phrase (those stay in the **impact metric**). Goal headline without numeric proof; goal proof in **`{{goal_metric}}`**. In the `then` clause use **we will** plus the goal as a **verb phrase** (e.g. GOAL *Grow monthly active players* becomes *then we will **grow monthly active players***), not *achieve **Grow …***. **Phrase naturally** (see Template); `by` is a default hook for the metric, not mandatory wording.  
- **Build lines:** same content as the scaffold (feature, actor, impact, impact metric); **phrase naturally** — see Template note below.  
- Names must match `impact-map.md`. Stakeholder file: filled hypothesis body only (no Instructions, no Example).  

## Notation  

- Section heading: `### Outcome` plus a short label (`{{outcome_section_goal_label}}` in Template only).  
- **Scaffold (required content, not fixed grammar):** outcome line = actor + impact + impact metric + `then we will` + goal as **verb phrase** + goal metric; roll-up = same pattern on broader goal; build line = feature + actor + impact + same impact metric as that cluster's outcome. Fill `{{goal_for_section}}` / `{{goal_broader}}` in the `then` clause as spoken verbs (**grow …**, **strengthen …**), not title case after *achieve*. Default stub uses `by` before the impact metric; rewrite for natural flow when filling.  
- Optional `PHASE: {{timebox}}` on its own line before the first build bullet for that timebox.  
- Repeat outcome + build groups under the same `###` when several impacts roll up to the same goal; start a new `### Outcome` when the roll-up goal changes.  

---  

## Template  

**When filling:** write **natural, readable sentences** — not mechanical repetition of one formula. Keep the same facts the placeholders stand for (actor, impact, impact metric, goal, goal metric on outcome lines; feature + the same impact metric on each build line). You may change connectors, order within the clause, and light wording so it sounds like something you would say in a review, without dropping or hiding any metric.  

```markdown  
<!-- When filling: natural sentences; `then we will` + verbal goal (grow / strengthen ...) + `with` + goal metric -- not "achieve **Grow ...**". Omit this comment from stakeholder files. -->  

### Outcome {{outcome_section_goal_label}}  

If **{{actor_1}}** **{{impact_1}}** by **{{impact_1_metric}}**, then we will **{{goal_for_section}}** with **{{goal_metric}}**.  

- If we build **{{feature_1a}}**, then **{{actor_1}}** will **{{impact_1}}** by **{{impact_1_metric}}**.  
- If we build **{{feature_1b}}**, then **{{actor_1}}** will **{{impact_1}}** by **{{impact_1_metric}}**.  

If **{{actor_1}}** **{{impact_2}}** by **{{impact_2_metric}}**, then we will **{{goal_for_section}}** with **{{goal_metric}}**.  

- If we build **{{feature_2a}}**, then **{{actor_1}}** will **{{impact_2}}** by **{{impact_2_metric}}**.  

If **{{actor_2}}** **{{impact_3}}** by **{{impact_3_metric}}**, then we will **{{goal_for_section}}** with **{{goal_metric}}**.  

- If we build **{{feature_3a}}**, then **{{actor_2}}** will **{{impact_3}}** by **{{impact_3_metric}}**.  

### Outcome {{broader_goal_section_label}}  

If **{{rollup_condition_short}}** by **{{rollup_impact_metric}}**, then we will **{{goal_broader}}** with **{{goal_metric_broader}}**.  
```  

(Add or remove `### Outcome` sections, outcome paragraphs, and build bullets per engagement.)  

---  

## Example (reference)  

**Audience:** Facilitators and agents — same live-ops engagement as **`impact-map.md`** Example (reference). Below is **stakeholder-shaped** copy: same actors, impacts, metrics, and deliverables as the tree, but phrased the way the Template asks (natural connectors, readable clauses — not placeholder paste).  

### Outcome Grow monthly active players  

If **Existing players** **share run highlights to social**, and **share attempts per active** move toward **~15%+ of players posting weekly**, then we will **grow monthly active players** with **verified MAU +20% vs last-quarter baseline this quarter**.  

- If we build **Share sheet with clip**, then **Existing players** will **share run highlights to social**, and **share attempts per active** should move toward **~15%+ of players posting weekly**.  
- If we build **Seasonal tournament badge (shareable moment)**, then **Existing players** will **share run highlights to social**, and **share attempts per active** should move toward **~15%+ of players posting weekly**.  
- If we build **Friend invite deep link**, then **Existing players** will **share run highlights to social**, and **share attempts per active** should move toward **~15%+ of players posting weekly**.  

If **Existing players** **complete challenges on schedule**, and **challenge completion among MAU** reaches toward **40%+**, then we will **grow monthly active players** with **verified MAU +20% vs last-quarter baseline this quarter**.  

- If we build **Streak and progress widget**, then **Existing players** will **complete challenges on schedule**, and **challenge completion among MAU** should reach toward **40%+**.  
- If we build **Push notification preferences (challenge nudges)**, then **Existing players** will **complete challenges on schedule**, and **challenge completion among MAU** should reach toward **40%+**.  

If **New players** **finish onboarding and first ranked run without dropping**, and **D1 / D7 retention** moves toward **45% / 25%**, then we will **grow monthly active players** with **verified MAU +20% vs last-quarter baseline this quarter**.  

- If we build **Skippable tutorial revamp**, then **New players** will **finish onboarding and first ranked run without dropping**, and **D1 / D7 retention** should move toward **45% / 25%**.  
- If we build **First-win bot match lane**, then **New players** will **finish onboarding and first ranked run without dropping**, and **D1 / D7 retention** should move toward **45% / 25%**.  

If **New players** **accept a friend or guild connection during onboarding**, and **social graph attach rate by D3** moves toward **30%**, then we will **grow monthly active players** with **verified MAU +20% vs last-quarter baseline this quarter**.  

- If we build **Suggested friends (consent-based contacts)**, then **New players** will **accept a friend or guild connection during onboarding**, and **social graph attach rate by D3** should move toward **30%**.  

If **Streamers and creators** **broadcast this title during the campaign window**, and **partner stream hours watched per week** move toward **50k+** while **broadcast cadence** holds at **at least twice per week**, then we will **grow monthly active players** with **verified MAU +20% vs last-quarter baseline this quarter**.  

- If we build **OBS overlay and scene kit**, then **Streamers and creators** will **broadcast this title during the campaign window**, and **partner stream hours watched per week** should move toward **50k+** and **broadcast cadence** should hold at **at least twice per week**.  
- If we build **Creator revenue-share tier**, then **Streamers and creators** will **broadcast this title during the campaign window**, and **partner stream hours watched per week** should move toward **50k+** and **broadcast cadence** should hold at **at least twice per week**.  

If **Platform moderators** **triage abuse and fraud reports**, and **median time to first moderator action** stays **under twelve hours (SLA)**, then we will **grow monthly active players** with **verified MAU +20% vs last-quarter baseline this quarter**.  

- If we build **Moderation queue dashboard**, then **Platform moderators** will **triage abuse and fraud reports**, and **median time to first moderator action** should stay **under twelve hours (SLA)**.  
- If we build **Assisted triage (auto-label suggestions)**, then **Platform moderators** will **triage abuse and fraud reports**, and **median time to first moderator action** should stay **under twelve hours (SLA)**.  

### Outcome Strengthen recurring revenue and engagement (flagship live-ops title)  

If **the modelled actor impacts move together**, and **each branch hits its impact metric band in the same window**, then we will **strengthen recurring revenue and engagement in the flagship live-ops title** with **net revenue from live ops +12% YoY**.  
