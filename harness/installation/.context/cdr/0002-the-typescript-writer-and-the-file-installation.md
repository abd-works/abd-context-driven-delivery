# The TypeScript toolset writer and the file installation stay one class each

The round-9 review (harness core, row 4) found *TypeScriptToolset* rebuilt a *_DataShape* on every call and wrote each shape's type text itself (39 methods, total complexity 105). *FileInstallation* (30 methods, total complexity 129) was judged one job.

## Decision

- Each class's *_DataShape* is made once for the file it is written into (`TypeScriptToolset.shape_of`), reads its fields once, and writes its own `export type` lines and the identity reference other data sends it by. The adapter's method writer is *AdapterMethod*, so *TypeScriptOperation* names only the TypeScript class model's operation.
- The writing of a hint's TypeScript type (`hint_type`, `identity_type`, `_reference_type`, `_shape_reference`, `_peer_data`) stays on *TypeScriptToolset*: the type of a hint depends on the file it is written into, its peer toolsets and the imports and nested shapes that file collects. After round 9 the class has 37 methods and total complexity 101. The next step is a part that holds one file's types (its peers, its imports, its nested shapes and the hint writing), made once per *TypeScriptToolset*, which leaves the toolset writing its classes, routes and header.
- *FileInstallation* writes one destination's files: every method serves that one channel's paths, front matter and body. It stays one class.
