# Impact map — ASCII wall sketch (markdown)  

## Instructions (for skill maintainers)  

- This file mirrors the **four-column impact map wall** used in **Lean-Agile Training** (Agile By Design): **Objective (Why?)**, **Persona (Who?)**, **Impact (How?)**, **Initiative (What?)** — same reading order as **`inputs/abd-answers-retrieval.md`** Kept chunks 1-3 and the prefix map in **`impact-map.md`** / **`impact-map.txt`**.  
- **Layout:** Pipe-separated columns. **Objective** holds the goal stack (broad then mapped sub-goals); use **`#`** on its own line under a goal in that column for **lagging proof** (same facts as **`METRIC:`** under a **`GOAL:`**). For each **actor / impact**, follow the wall map order: a row with **Persona** and **Impact** and an empty **Initiative** cell; then an optional row with **`#`** only in the **Impact** column (behaviour proxy, same fact as **`METRIC:`** under that **`IMPACT:`**); then one row per **`DELIVERABLE:`** (repeat persona and impact on each initiative row). Leave **Persona** empty on **`#`** metric rows.  
- Fill the **Template** block: replace every `{{placeholder}}`. Use **ASCII only** (no Unicode box drawing). Stakeholder deliverable = filled table (column headers optional if the room already has a poster; keep **`#`** metric rows).  
- **Parity:** Same goals, actors, impacts, metrics, and initiatives as **`impact-map.md`** / **`impact-map.txt`**; this is the **same map** in slide-style columns, not a different story.  

## Notation  

- **OBJECTIVE column:** Top = broad **`GOAL:`** headline; optional **`#`** line = lagging proof; then mapped **`GOAL:`**; optional **`#`** lines for each **`METRIC:`** under that goal in the hierarchy.  
- **PERSONA / IMPACT / INITIATIVE columns:** One **initiative** row per **`DELIVERABLE:`** line; repeat persona and impact text when the same behaviour has several deliverables.  
- **`#` (impact):** Behaviour or usage proxy for that impact only; place it **before** the initiative rows for that impact; omit if there is no impact metric in the hierarchy.  
- **NOTE / ASSUMPTION:** Same as prefix map; place **`NOTE:`** / **`ASSUMPTION:`** in the Objective column after the goal stack, or below the table.  

---  

## Template  

```text  
OBJECTIVE (Why?) | PERSONA (Who?) | IMPACT (How?) | INITIATIVE (What?)  
-----------------+----------------+---------------+--------------------  
{{ascii_goal_broad}} | | |  
  # {{ascii_metric_broad_optional}} | | |  
{{ascii_goal_mapped}} | | |  
  # {{ascii_metric_mapped_1}} | | |  
  # {{ascii_metric_mapped_2_optional}} | | |  

| {{ascii_actor_1}} | {{ascii_impact_1_1}} |  
| | | # {{ascii_impact_metric_1_1}}  
| {{ascii_actor_1}} | {{ascii_impact_1_1}} | {{ascii_init_1_1a}}  
| {{ascii_actor_1}} | {{ascii_impact_1_1}} | {{ascii_init_1_1b}}  
| {{ascii_actor_1}} | {{ascii_impact_1_2}} |  
| | | # {{ascii_impact_metric_1_2}}  
| {{ascii_actor_1}} | {{ascii_impact_1_2}} | {{ascii_init_1_2a}}  
| {{ascii_actor_2}} | {{ascii_impact_2_1}} |  
| | | # {{ascii_impact_metric_2_1}}  
| {{ascii_actor_2}} | {{ascii_impact_2_1}} | {{ascii_init_2_1a}}  
| {{ascii_actor_3}} | {{ascii_impact_3_1}} |  
| | | # {{ascii_impact_metric_3_1}}  
| {{ascii_actor_3}} | {{ascii_impact_3_1}} | {{ascii_init_3_1a}}  

{{ascii_note_optional}}  
```  

(Add or remove persona / impact / initiative rows per engagement. Drop **`#`** metric rows when unused.)  

---  

## Example (reference)  

**Audience:** Facilitators and agents — same fictional live-ops engagement as **`impact-map.md`** Example (reference); columns match the training wall map shape.  

```text  
OBJECTIVE (Why?) | PERSONA (Who?) | IMPACT (How?) | INITIATIVE (What?)  
-----------------+----------------+---------------+--------------------  
Strengthen recurring revenue and engagement in the flagship live-ops title | | |  
  # Net revenue from live ops +12% YoY; engagement targets for the title | | |  
Grow monthly active players | | |  
  # Verified MAU +20% vs last-quarter baseline this quarter (strategic adoption) | | |  
  # Net revenue from live ops +12% YoY (economic) | | |  
NOTE: M1-M4 below = calendar months in this example; use quarters if the brief says Q1-Q4 instead. | | |  
ASSUMPTION: Moderator SLA stays feasible at projected creator stream volume; re-check if partner hours watched doubles before M3. | | |  

| Existing players | Share run highlights to social |  
| | | # % of actives posting any share weekly; target 15%+  
| Existing players | Share run highlights to social | Share sheet with clip  
| Existing players | Share run highlights to social | Seasonal tournament badge (shareable moment)  
| Existing players | Share run highlights to social | Friend invite deep link  
| Existing players | Complete challenges on schedule |  
| | | # Challenge completion rate among MAU; target 40%+  
| Existing players | Complete challenges on schedule | Streak and progress widget  
| Existing players | Complete challenges on schedule | Push notification preferences (challenge nudges)  
| New players | Finish onboarding and first ranked run without dropping |  
| | | # D1 / D7 retention; targets 45% / 25%  
| New players | Finish onboarding and first ranked run without dropping | Skippable tutorial revamp  
| New players | Finish onboarding and first ranked run without dropping | First-win bot match lane  
| New players | Accept a friend or guild connection during onboarding |  
| | | # Social graph attach rate by D3; target 30%  
| New players | Accept a friend or guild connection during onboarding | Suggested friends (consent-based contacts)  
| Streamers and creators | Broadcast this title during the campaign window |  
| | | # Partner stream hours watched per week; target 50k+; broadcast cadence at least twice per week  
| Streamers and creators | Broadcast this title during the campaign window | OBS overlay and scene kit  
| Streamers and creators | Broadcast this title during the campaign window | Creator revenue-share tier  
| Platform moderators | Triage abuse and fraud reports |  
| | | # Median time to first moderator action; target under 12 hours (SLA)  
| Platform moderators | Triage abuse and fraud reports | Moderation queue dashboard  
| Platform moderators | Triage abuse and fraud reports | Assisted triage (auto-label suggestions)  

NOTE: M1-M4 phased rows for this engagement match the **Actor / impact** column in impact-map.md Example (reference); use the same **actor / impact** text there.  
```  
