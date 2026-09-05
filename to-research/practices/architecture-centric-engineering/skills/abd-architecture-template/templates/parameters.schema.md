<!--
  Meta-template: shape of the parameters.json file inside a generated
  template package.

  DELETE this leading "Meta-template:" instruction block if you adapt this
  file for inclusion in a generated package.
-->

# `parameters.json` schema

`parameters.json` lives at the root of every generated template package. It is the **declarative** description of:

1. Every placeholder the template defines.
2. The rename map (which placeholders also appear in filenames).
3. The sentinel binding `example/` uses.

`abd-architecture-code` reads this file to know what to substitute and where.

## Schema

```json
{
  "sourceMechanism": "<string>",
  "sourceContextFile": "<workspace-root path>",
  "placeholders": [
    {
      "name": "<string>",
      "bindsTo": "<string>",
      "scope": "identifier | filename | both",
      "example": "<string>"
    }
  ],
  "renameMap": [
    { "from": "<string>", "to": "<string>" }
  ],
  "sentinel": {
    "name": "<string>",
    "bindings": {
      "<placeholderName>": "<sentinelValue>"
    }
  }
}
```

## Field reference

| Field | Purpose | Example |
|---|---|---|
| `sourceMechanism` | Name of the mechanism whose `architecture-context.md` is the source. Match the spec's Mechanisms one-liner. | `"Partner Integrations"` |
| `sourceContextFile` | Workspace-root path to the source `architecture-context.md`. | `/src/integrations/architecture-context.md` |
| `placeholders[].name` | Placeholder token as it appears in `template/` files. Match the source spec verbatim. | `"{Domain}"` |
| `placeholders[].bindsTo` | One-line description of what kind of value the code skill should substitute. | `"domain entity name (e.g. Recipient)"` |
| `placeholders[].scope` | Where this placeholder appears: in code identifiers, in filenames, or both. | `"both"` |
| `placeholders[].example` | The value `example/` uses. Sourced from the sentinel binding. | `"Recipient"` |
| `renameMap[]` | Filename rewrites the code skill must apply when copying `template/` files. One entry per file whose name uses a placeholder. | `{ "from": "{Domain}.ts", "to": "<Domain>.ts" }` |
| `sentinel.name` | The single sentinel identity `example/` binds against. Unmistakeably unreal. | `"ExampleCo"` |
| `sentinel.bindings` | Concrete substitution map from placeholder names to sentinel values. | `{ "{Domain}": "ExampleProduct" }` |

## Worked example

```json
{
  "sourceMechanism": "Partner Integrations",
  "sourceContextFile": "/src/integrations/architecture-context.md",
  "placeholders": [
    {
      "name": "{System}",
      "bindsTo": "partner system name (PascalCase)",
      "scope": "both",
      "example": "ExampleCoPartner"
    },
    {
      "name": "{operation}",
      "bindsTo": "operation name in camelCase (verb-noun)",
      "scope": "identifier",
      "example": "submitOrder"
    },
    {
      "name": "{Feature}",
      "bindsTo": "story sub-epic slug",
      "scope": "both",
      "example": "submitOrder"
    }
  ],
  "renameMap": [
    { "from": "{System}Handler.ts", "to": "<System>Handler.ts" },
    { "from": "{System}Payload.ts", "to": "<System>Payload.ts" },
    { "from": "{System}.config.ts", "to": "<System>.config.ts" }
  ],
  "sentinel": {
    "name": "ExampleCo",
    "bindings": {
      "{System}": "ExampleCoPartner",
      "{operation}": "submitOrder",
      "{Feature}": "submitOrder"
    }
  }
}
```

## Rules

- Every placeholder used in `template/` or `templates/tests/` MUST appear in `placeholders[]`. Missing declarations are a violation against [`../rules/template-uses-spec-placeholders.md`](../rules/template-uses-spec-placeholders.md).
- Every placeholder used in a filename MUST also appear in `renameMap[]` with a `to` value that the code skill can substitute against.
- `sentinel.bindings` MUST cover every entry in `placeholders[]`. `example/` cannot be built otherwise.
- Placeholder `name` values MUST match the source `architecture-context.md` Canonical Patterns verbatim — no normalisation, no renaming.
