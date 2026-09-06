# Input traps — abd-architecture-blueprint

Assumptions, ambiguities, and missing context that commonly produce a weak blueprint. Check each trap against available input before generating — flag gaps honestly; do not invent modules or mechanisms to fill them.

- **Mechanism code shape** — for each mechanism we're naming, can you describe the concrete constraint it places on code — or is it still just a label? If you can't say what a developer must do differently because of this mechanism, it isn't blueprint-ready.
- **Module boundaries vs. business scope** — are these modules drawn around business capabilities, or are they just reflecting folder structure or framework conventions? What would break if you merged two of them or split one?
- **Runtime flow vs. assumed flow** — when you trace a request through the mechanisms, are you describing how this system actually behaves, or how systems like this typically behave? Where would you be surprised if you watched real traffic?
- **Mechanism overlap** — are any two mechanisms doing the same work at different layers, or is there a gap between them where no mechanism owns the concern? What falls through?
- **Testing tiers vs. team reality** — do the test tiers in this blueprint match how the team actually tests, or are they an idealized model? Which tier is the team least likely to write, and what risk does that leave uncovered?
