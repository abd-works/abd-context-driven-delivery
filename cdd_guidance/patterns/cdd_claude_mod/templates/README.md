# Claude Code mod templates

Scaffold for one domain component of a mod that views the CDD domain. Replace `{domain}` with the component's folder and toolset name, such as `kanban`, `{Object}` and `{object}` with the Python class the client mirrors, such as `Ticket`, and `{screen}` with the view's name. Each object a person acts on gets its own client file.

```
templates/
└── {domain}/
    └── pane/
        ├── .claude-plugin/plugin.json    ← names the mod and its contract
        ├── types/index.d.ts              ← PluginState; {Object}Data comes from the language adapter
        └── hooks/
            ├── hooks.json                ← names register.tsx
            ├── register.tsx              ← Boot: events only
            └── {domain}/
                ├── {object}-client.ts    ← {Object}Client for display, its actions one mcp call each
                └── {screen}-view.tsx     ← {Screen}View: a plain function painting the client
```

The Python toolset is not templated. Annotate the domain class itself, so its tools read `{object}.{operation}`.
