# Claude Code mod templates

Scaffold for one domain component of a mod that views the CDD domain. Replace `{domain}` with the kebab-case folder name, `{Domain}` with the Python class name, and `{screen}` with the view's name.

```
templates/
└── {domain}/
    └── pane/
        ├── .claude-plugin/plugin.json    ← names the mod and its contract
        ├── types/index.d.ts              ← {Domain}Json and PluginState
        └── hooks/
            ├── hooks.json                ← names register.tsx
            ├── register.tsx              ← Boot: events only
            └── {domain}/
                ├── {domain}-client.ts    ← {Domain}Client: mirrors Python, one mcp call
                └── {screen}-view.tsx     ← {Screen}View: paints the client
```

The Python toolset is not templated: follow `harness/kanban/kanban.py`.
