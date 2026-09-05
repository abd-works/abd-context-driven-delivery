# Input traps — abd-architecture-outline

Assumptions, ambiguities, and missing context that commonly produce a weak outline. Check each trap against available input before generating — flag gaps honestly; do not invent systems or mechanisms to fill them.

- **System identity** — when someone says "the system," do all stakeholders picture the same boundary? What gets left out when you draw the box, and what gets accidentally included?
- **Hidden neighbors** — are there systems, services, or manual processes that interact with this system that nobody has mentioned yet? The ones that surface during integration are the ones nobody named during shaping. The surrounding-systems table must be complete; a missing row is a hidden architectural dependency.
- **Mechanism as pattern** — for each candidate mechanism, can you name the principle, the pattern, and at least two concrete things in this system that will follow it? If not, it is not a mechanism for this system — it is either a one-off (belongs in a package description), a deferred concern, or absent. The standard vocabulary is a discovery prompt, not a checklist.
- **Connection assumptions** — for each arrow between systems, do you know the protocol, who initiates, and what happens when the other side is unavailable? Or are those details being deferred without anyone tracking the deferral?
- **Rules vs. preferences** — can each rule in the Rules section be applied to a real code change with a clear yes-or-no answer, or is it a sentiment that sounds wise but doesn't constrain anything? If you can't fail a PR against it, it's not a rule.
- **What's deliberately excluded** — what have you decided is out of scope for this outline, and does the team agree it's out of scope — or are they assuming someone else is covering it?
