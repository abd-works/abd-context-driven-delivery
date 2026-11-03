# CDD web domain access templates

What an application writes for a domain object reached from TypeScript. Replace `{Object}` and `{object}` with the Python class, such as `Ticket` and `ticket`, `{context}` with the bounded context folder, `{source folders}` with the folders the Python sits in, and `{Page}` with the page object that wires the page's clients.

```
templates/
└── src/
    ├── cdd/
    │   └── cdd-routes.ts               ← one per application: mounts every generated {object}Routes
    └── {context}/{object}/
        └── {object}-client.tsx         ← {Object}Client extends {Object}ClientGenerated: what only the page knows
```

`{Object}Data`, `{Object}`, `{Object}Adapter`, `{Object}ClientGenerated`, `{object}Routes`, and `CddConnection` are not templated, because the installer writes them to `<install path>/language-adapters/typescript/` from the Python. Mark the domain class with `@language_adapter(language="typescript", identity=...)`, annotate `to_json()` with a `TypedDict`, and install.
