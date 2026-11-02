# CDD access templates

Scaffold for one domain object reached from a TypeScript server. Replace `{Object}` and `{object}` with the Python class, such as `Ticket` and `ticket`, `{context}` with the bounded context folder, and `{domain}` with the Python folder.

```
templates/
└── src/
    ├── cdd/
    │   └── cdd-connection-node.ts      ← one per application: starts cdd and carries calls
    └── {context}/{object}/
        ├── {object}-node.ts            ← {Object}Node extends {Object}Tools
        └── {object}-routes.ts          ← asks the node
```

`{Object}`, `{Object}Data`, and `{Object}Tools` are not templated, because the installer writes them to `<install path>/language-adapters/typescript/` from the Python. Mark the domain class with `@language_adapter(language="typescript")`, annotate `to_json()` with a `TypedDict`, and install.
