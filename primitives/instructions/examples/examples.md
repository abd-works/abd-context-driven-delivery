# Instruction slot examples

## RecipeGuide — all three instruction forms

`RecipeGuide` is a minimal toolset that demonstrates every way to supply instruction content to an `@action`.

**Form A — inline prose** (`brainstorm` action)
String literals in the `@action` body are the instruction text. `{{expr}}` substitutions resolve against the live instance. No `@instruction` slot required.

**Form B — named slot → section** (`technique` slot)
`@instruction def technique` resolves to the `## Technique` heading in `recipe_guide.md` because the method name (`technique`) matches a heading in the kit doc. No `label=` needed.

**Form C — named slot → file** (`plating` slot)
`@instruction(label="plating-rules") def plating` resolves to `plating-rules.md` beside the package. The `label=` kwarg is required here because the filename contains a hyphen.

### Cuisine examples

| cuisine | theme |
|---|---|
| French | summer vegetables |
| Japanese | umami-forward comfort food |
| Mexican | weeknight pantry meals |
