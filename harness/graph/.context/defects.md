# Defects

- **Practices opened fully expanded.** The tree stays collapsed until a node is opened.
  - Test, line 182: [should leave every practice collapsed until it is opened](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Vitest: 15 passed.

- **One invoke child hidden.** Both invoke children render under the operation.
  - Test, line 205: [should list every invoke under an operation](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Vitest: 15 passed.

- **Folder control would not accept a directory.** Choose folder writes the path and loads that working copy.
  - Test, line 300: [should put the chosen folder on the page and show its classes](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Vitest: 15 passed. Mocks `choose_folder`. Does not open the operating-system dialog.

- **Last folder forgotten on restart.** Stored in `cdd-graph-folder` and loaded on open.
  - Test, line 310: [should reload the last folder when the app opens](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Vitest: 15 passed.

- **Source canvas ate the mouse wheel.** Monaco scrollbar uses `handleMouseWheel: false` and `alwaysConsumeMouseWheel: false` in `app/source/SourceView.tsx`.
  - Test, line 262: [should fold calls, classes, and blocks in the source](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Opening register goes through `SourceClient`, and the test reads the scrollbar options the view passes to the editor.

- **Class fold missing on a variable of a class type.** `variableTypes` in `app/source/call-expansion.ts` records the binding and folds that class under the line.
  - Test, line 262: [should fold calls, classes, and blocks in the source](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). The register fixture declares `const account: AccountToken`. The test reads `.call-fold`, `.class-fold`, and `.block-fold` on those lines in the editor.

- **Violations switch ignored rule failures.** Turning it on sends `return_nodes` with `violations: true`.
  - Test, line 323: [should send violations when the switch is turned on](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Vitest: 15 passed.

- **Create, merge, and reload called the wrong operation.** They call `create_database`, `reload_working_copy`, and `load_working_copy`.
  - Test, line 332: [should create the database for the chosen folder](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Test, line 340: [should merge the working copy onto master](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Test, line 348: [should reload the working copy for the chosen folder](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx). Vitest: 15 passed. They mock the host and do not extract a database.

- **Create database left the existing database in place.** `create_database` deletes the master, the working copy, and the stamp, then extracts again.
  - Test, line 31: [should store the master beside the sample](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_database_spec.py). Test, line 35: [should store the working copy beside the sample](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_database_spec.py). Not run after the change. Running it deletes `examples/input/.codeql` and extracts the sample.

- **Parameter listed twice.** Removed TypeScript `operation-owns-parameters.ql`. The parameter stays under `hasParameter`.
  - Test, line 138: [should parent the parameter on its operation through hasParameter](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Not run after the query was removed.

- **Steps missing invokes, scopes, observes, demonstrates, and retrievedUsing.** Then steps are included. The receiver is the annotated type, `this`, or a unique method name. Const examples such as `emailedValidationCode` are example nodes, so an observes edge can attach.
  - Test, line 285: [should parent the example on scopes](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 290: [should parent scopes on the step](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 299: [should place that operation under the step](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 303: [should place that step back under the operation](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 311: [should place that example under observes](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 314: [should parent observes on the step](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 322: [should place that class under demonstrates](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 325: [should place that example back on the class](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 333: [should place that property under retrievedUsing](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Test, line 336: [should parent retrievedUsing on the example](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py). Mamba: 106 examples ran. Retrieved-using operations still return no rows.

- **Module, package, and aggregate ids were bare names.** `moduleId`, `packageId`, and `aggregateId` are path ids (`clean_engineering:Module:src/customer`, `ddd:Aggregate:src/customer`).
  - Hand check: `codeql bqrs decode` on the pml-web working copy. `module-owns-classes.bqrs` lists the customer classes under that module id. No test asserts the id string. This did not fill the customer folder. Serialization did.

- **Customer empty in clean engineering and DDD.** `serialize` writes children on the home parent. A `belongsTo` copy stays a name.
  - Hand check: Python load of the pml-web working copy. Customer module children: CustomerClient, CustomerNode, Address, Customer, CustomerException, CustomerRepository, Identity, asCustomerNode. Customer aggregate children: Customer, CustomerRepository, Address, Identity. `belongsTo` copies empty.
  - Line 191: [should show the customer aggregate with its entity, repository, and value objects](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/app/app.test.tsx) uses a fixture that already has those children. It does not call `serialize`.
  - Line 360: [should own account-credentials and customer under the bounded context](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py) and line 392: [should parent the entity root on its aggregate](C:/dev/abd-context-driven-delivery/harness/codeQl_graph/codeql_graph_spec.py) read the in-memory graph, which already had the children.

## Not fixed

- **Scenario and step order.** Given, when, then, and and/but follow the source line. Queries order by file and line. `populate` writes that order, and `serialize` keeps it.
- **Reload ignores query edits when a `.bqrs` file exists.** It does not compare query text to that file. No code change.
