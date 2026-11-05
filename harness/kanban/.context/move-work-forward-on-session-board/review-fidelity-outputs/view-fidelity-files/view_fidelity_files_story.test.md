# (E) Move Work Forward On Session Board
## (E) Review Fidelity Outputs
### (S) Person --> View Fidelity Files

#### Scenario: Open one tab per format, generated or not

*Given* checkout-flow's story map is tests/story-map.md and tests/story-map.drawio is not there
*When* the Person views checkout-flow's story_map files
*Then* the files panel shows the tabs tests/story-map.md and tests/story-map.drawio
*And* the tests/story-map.md tab shows # Check Out Order
*And* the drawio tab says it is not generated yet

#### Scenario: Go back to the list when the last tab closes

*Given* the tabs tests/story-map.md and tests/story-map.drawio are open
*When* the Person closes both tabs
*Then* the files panel shows the list

#### Scenario: Refuse a file outside the repository

*Given* checkout-flow's repository is the project folder
*When* a file outside the repository is asked for
*Then* the board says ../secrets.txt is not a file in this repository
