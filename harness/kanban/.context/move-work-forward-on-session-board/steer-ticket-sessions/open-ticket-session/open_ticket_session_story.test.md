# (E) Move Work Forward On Session Board
## (E) Steer Ticket Sessions
### (S) Person --> Open Ticket Session

#### Scenario: Open a new ticket

*Given* checkout-flow is the active [ticket](../../../kanban-model.md#ticket--card)
*When* the Person opens a new ticket titled Pet visits
*Then* pet-visits is In progress in Discovery, titled Pet visits
*And* its next step is Generate on stories-story_map
*And* checkout-flow is still the active ticket

#### Scenario: Ask a chat to open a ticket

*Given* a chat is connected to the session board
*When* the Person asks for a new ticket from the board's header
*Then* the chat's prompt holds Open a new ticket with ticket.create, titled: for the Person to finish

#### Scenario: Keep + Ticket off with no chat

*Given* no chat is connected to the session board
*When* the session board draws its header
*Then* + Ticket is off

#### Scenario: Open a ticket on a folder of the repository

*Given* the [repository](../../../kanban-model.md#repo) has the folder src/billing
*When* the Person opens a ticket titled Billing report on src/billing
*Then* billing-report's [session](../../../kanban-model.md#session) works in src/billing
*And* the details show its workpath as src/billing

#### Scenario: Choose a ticket's workpath

*Given* checkout-flow works on the whole [repository](../../../kanban-model.md#repo)
*And* the repository has src/billing and src/visits under src
*When* the Person browses src for checkout-flow's workpath
*Then* the roots dialog lists src/billing and src/visits
*When* the Person chooses src/visits as checkout-flow's workpath
*Then* checkout-flow's workpath reads src/visits
*And* each practice's default practice root sits under src/visits

#### Scenario: Choose one practice's root and go back to its default

*Given* checkout-flow's Stories [practice](../../../kanban-model.md#practiceguidance) writes under its default root
*When* the Person chooses src/billing for checkout-flow's Stories root
*Then* the Stories root reads src/billing, chosen by the Person
*And* every other practice stays on its default root
*When* the Person puts Stories back on its default root
*Then* the Stories root is the default again
