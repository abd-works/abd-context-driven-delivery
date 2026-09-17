# sub_agent

- `@sub_agent` still marks a method. Do not re-attach discovery through `ToolsetExtensions` — that registry is gone with `primitives/installer/extensions.py`.
- `register()` is a no-op. Do not import `primitives.installer.extensions`.
