# Impact map (markdown)  

## Instructions (for skill maintainers)  

- Fill the **Template** section: replace every `{{placeholder}}` with engagement content. Do not paste this Instructions block into stakeholder deliverables.  
- Goal — Broader to finer; one `GOAL:` per level. Actors under the mapped `GOAL:`.  
- Keep each `GOAL:` and `IMPACT:` line **behavioural / directional only** — no embedded cadence (e.g. weekly), deadlines (e.g. by day 3), thresholds, or SLA timing. Put those on `METRIC:` lines under the right parent (`GOAL:` vs `IMPACT:`).  
- `METRIC:`, `NOTE:`, `ASSUMPTION:` optional per `SKILL.md`.  
- Repeat `ACTOR:` / `IMPACT:` / `DELIVERABLE:` blocks as needed; add or remove deliverable lines per impact.  

## Notation  

- Goal — `GOAL:`; directional outcome in the world.  
- Metric (goal) — `METRIC:` indented under a `GOAL:`; lagging proof for that goal (one or more lines).  
- Actor — `ACTOR:`; situational who.  
- Impact — `IMPACT:`; observable behaviour.  
- Metric (impact) — `METRIC:` indented under an `IMPACT:`; behaviour or usage proxy (optional).  
- Deliverable — `DELIVERABLE:`; option under impact (one or more).  

---  

## Template  

```text  
GOAL: {{goal_broad}}  
GOAL: {{goal_mapped}}  
  METRIC: {{goal_metric_1}}  
  METRIC: {{goal_metric_2}}  
  NOTE: {{note_timebox_convention}}  
  ASSUMPTION: {{assumption_or_none}}  
  ACTOR: {{actor_1_label}}  
    IMPACT: {{actor_1_impact_1}}  
      METRIC: {{actor_1_impact_1_metric}}  
      DELIVERABLE: {{actor_1_impact_1_deliverable_a}}  
      DELIVERABLE: {{actor_1_impact_1_deliverable_b}}  
    IMPACT: {{actor_1_impact_2}}  
      METRIC: {{actor_1_impact_2_metric}}  
      DELIVERABLE: {{actor_1_impact_2_deliverable_a}}  
  ACTOR: {{actor_2_label}}  
    IMPACT: {{actor_2_impact_1}}  
      METRIC: {{actor_2_impact_1_metric}}  
      DELIVERABLE: {{actor_2_impact_1_deliverable_a}}  
```  

Feature backlog (phased) — optional; each row names **phase**, **feature**, and **actor / impact** (same pair as one branch in the tree above):  

| Phase | Feature | Actor / impact |  
| --- | --- | --- |  
| {{phase_1}} | {{feature_1}} | {{actor_impact_1}} |  
| {{phase_2}} | {{feature_2}} | {{actor_impact_2}} |  

---  

## Example (reference)  

**Audience:** Facilitators and agents — same fictional live-ops engagement as **`SKILL.md`** Example; mirror depth and prefix discipline, not these literal product names.  

```text  
GOAL: Strengthen recurring revenue and engagement in the flagship live-ops title  
GOAL: Grow monthly active players  
  METRIC: Verified MAU +20% vs last-quarter baseline this quarter (strategic adoption)  
  METRIC: Net revenue from live ops +12% YoY (economic)  
  NOTE: M1-M4 below = calendar months in this example; use quarters if the brief says Q1-Q4 instead.  
  ASSUMPTION: Moderator SLA stays feasible at projected creator stream volume; re-check if partner hours watched doubles before M3.  

  ACTOR: Existing players  
    IMPACT: Share run highlights to social  
      METRIC: % of actives posting any share weekly; target 15%+  
      DELIVERABLE: Share sheet with clip  
      DELIVERABLE: Seasonal tournament badge (shareable moment)  
      DELIVERABLE: Friend invite deep link  
    IMPACT: Complete challenges on schedule  
      METRIC: Challenge completion rate among MAU; target 40%+  
      DELIVERABLE: Streak and progress widget  
      DELIVERABLE: Push notification preferences (challenge nudges)  

  ACTOR: New players  
    IMPACT: Finish onboarding and first ranked run without dropping  
      METRIC: D1 / D7 retention; targets 45% / 25%  
      DELIVERABLE: Skippable tutorial revamp  
      DELIVERABLE: First-win bot match lane  
    IMPACT: Accept a friend or guild connection during onboarding  
      METRIC: Social graph attach rate by D3; target 30%  
      DELIVERABLE: Suggested friends (consent-based contacts)  

  ACTOR: Streamers and creators  
    IMPACT: Broadcast this title during the campaign window  
      METRIC: Partner stream hours watched per week; target 50k+; broadcast cadence at least twice per week  
      DELIVERABLE: OBS overlay and scene kit  
      DELIVERABLE: Creator revenue-share tier  

  ACTOR: Platform moderators  
    IMPACT: Triage abuse and fraud reports  
      METRIC: Median time to first moderator action; target under 12 hours (SLA)  
      DELIVERABLE: Moderation queue dashboard  
      DELIVERABLE: Assisted triage (auto-label suggestions)  
```  

| Phase | Feature | Actor / impact |  
| --- | --- | --- |  
| M1 | Share sheet with clip | Existing players / Share run highlights to social |  
| M1 | Skippable tutorial revamp | New players / Finish onboarding and first ranked run |  
| M1 | Moderation queue dashboard | Platform moderators / Triage abuse and fraud reports |  
| M2 | Friend invite deep link | Existing players / Share run highlights to social |  
| M2 | First-win bot match lane | New players / Finish onboarding and first ranked run |  
| M3 | Seasonal tournament badge | Existing players / Share run highlights to social |  
| M3 | Creator revenue-share tier | Streamers / Broadcast during campaign |  
| M4 | Push notification preferences | Existing players / Complete challenges on schedule |  
| M4 | Assisted triage (auto-label) | Platform moderators / Triage abuse and fraud reports |  
| M4 | Suggested friends (consent-based) | New players / Friend or guild connection during onboarding |  
