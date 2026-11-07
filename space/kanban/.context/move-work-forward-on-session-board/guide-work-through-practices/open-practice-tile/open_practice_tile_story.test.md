# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Person --> Open Practice Tile

#### Scenario: Open a tile on a short hover

*Given* billing-report's card is expanded
*When* the Person rests the pointer on the story_map tile for half a second
*Then* the story_map tile's action bar opens above the grid, at full width
*When* the Person moves the pointer away
*Then* the action bar closes

#### Scenario: Keep a pressed tile open

*Given* billing-report is selected
*When* the Person presses the story_map tile
*Then* the story_map action bar stays open after the pointer leaves
*When* the Person presses the story_map tile again
*Then* the story_map action bar closes

#### Scenario: Keep two pressed tiles open at once

*Given* billing-report's story_map tile is pressed open
*When* the Person presses the bounded_context tile
*Then* both action bars are open
*When* the Person chooses sketch on the bounded_context bar
*Then* only the bounded_context bar's action is sketch

#### Scenario: Open a hovered tile beside a pressed one

*Given* billing-report's card is expanded with the story_map tile pressed open
*When* the Person hovers on the ia tile
*Then* the ia bar opens beside the story_map bar
*When* the Person moves the pointer away from the ia tile
*Then* the ia bar closes and the story_map bar stays open

#### Scenario: Leave a tile in the details closed under a resting pointer

*Given* billing-report is shown in the details
*When* the Person rests the pointer on the story_map tile in the details
*Then* the story_map action bar stays closed
