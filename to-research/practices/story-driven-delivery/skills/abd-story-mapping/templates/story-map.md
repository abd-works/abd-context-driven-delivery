<!-- Pair required: also produce `story-map.txt` with the same tree. See SKILL.md → "Use every template file (required)". -->    
  
<!-- Pair required: also produce `story-map.txt` with the same tree. See SKILL.md → "Use every template file (required)". -->    
  
(E) Epic Name    
    (E) Sub-Epic Name    
        (E) Nested Sub-Epic Name (optional)    
            (S) Actor --> Story Name    
            (S) Actor --> Story Name    
            or (S) Actor --> Story Name    
                (AC) Actor --> Acceptance Criteria    
                (AC) Actor --> Acceptance Criteria    
            (S) Actor --> Story Name    
                (AC) Actor --> Acceptance Criteria    
                (AC) Actor --> Acceptance Criteria    
        (E) Another Nested Sub-Epic Name    
            (S) Actor --> Story Name    
            (S) Actor --> Story Name    
  
(E) {epic_name}    
    (E) {sub_epic_name}    
        (S) {actor} --> {story_name}    
        (S) {actor} --> {story_name}    
        or (S) {actor} --> {story_name}    
            (AC) {actor} --> {acceptance_criteria}    
            (AC) {actor} --> {acceptance_criteria}    
            (S) {actor} --> {story_name}    
                (AC) {actor} --> {acceptance_criteria}    
                (AC) {actor} --> {acceptance_criteria}    
        (S) {actor} --> {story_name}    
  
<!-- Notation below is for skill/template maintainers. Agents MUST NOT copy this section into generated story-map.md files in projects. -->    

## Instructions (template reference only — omit from generated maps)    

- **Epics (E)**: Top-level features, no connectors    
- **Sub-Epics (E)**: Nested epics, no connectors    
- **Stories (S)**: User stories with actors, format: `Actor --> Story Name`    
- **Acceptance Criteria (AC)**: Nested under stories, format: `Actor --> Acceptance Criteria`    
- **Context Gaps**: Use `* Gap:` inline under the relevant node, or a `## Context Gaps` section at the bottom for map-wide gaps. Both placements can coexist.    
- **Connectors**:    
  - "and" is the default - do NOT show in output (only stored in JSON)    
  - "or" shown explicitly for alternatives    
  - "opt" shown explicitly for optional items    
- **Indentation**: Use spaces (4 spaces per level), not tabs    
- **First item**: No connector (even if default "and")    
- **Nesting**: Stories can contain nested stories or acceptance criteria    
- **Language**: Use active behavioral language (verb-noun format)    
- **Epic/Sub-Epic names**: Verb-Noun format (actor NOT in name)    
- **Story/AC names**: Actor-Verb-Noun format (actor shown with "-->")  
