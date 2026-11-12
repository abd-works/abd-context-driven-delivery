# Share read-only projects in the board tools spec

An earlier agent started making `space/kanban/kanban_tools_spec.py` faster by giving contexts that only read one shared project, made once in `before.all`, instead of a new project for every example. It was left uncommitted in the worktree `.claude/worktrees/agent-a118638718fa6d28f`, which was removed on 2026-11-12, so the change is kept here. It is against the spec as it was before 57bbb61d1 trimmed it, so it needs redoing on the current file rather than applying as it is.

```diff
diff --git a/space/kanban/kanban_tools_spec.py b/space/kanban/kanban_tools_spec.py
index b377c1db4..a9812312a 100644
--- a/space/kanban/kanban_tools_spec.py
+++ b/space/kanban/kanban_tools_spec.py
@@ -36,9 +36,23 @@ from space.session.session import UnknownPracticeError  # noqa: E402
 from space.kanban.board_tools_examples import CHECKED_GRAPH, DISCOVERY_DONE, JUDGED_REPORT, ProjectTools, STORY_MAP_GRAPH, WHOLE_STORIES_GRAPH, next_action_of, reports_of, session_file_of, violation_counts_of  # noqa: E402
 
 
+def _with_violations(project: ProjectTools) -> ProjectTools:
+    """project with a ticket whose story map was generated and validated with a violation left."""
+    project.ticket(
+        "sign-up",
+        "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
+        "2026-10-31T01:00:01Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
+        title="Sign up",
+    )
+    return project
+
+
 with description("the board tools") as self:
+    # An example that changes what another would see gets a project of its own; a context whose examples only read
+    # shares one project, made once in its before.all (shared_project).
     with before.each:
-        self.project = ProjectTools()
+        if not getattr(self, "shared", False):
+            self.project = ProjectTools()
 
     with after.each:
         os.environ.pop("CDD_PROJECT", None)
@@ -805,7 +819,8 @@ with description("the board tools") as self:
 
     # (S) Person --> Send Next Fidelity Action
     with context("with a ticket whose story map has passed validate"):
-        with before.each:
+        with before.all:
+            self.shared, self.project = True, ProjectTools()
             self.project.ticket(
                 "sign-up",
                 "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
@@ -813,6 +828,9 @@ with description("the board tools") as self:
                 title="Sign up",
             )
 
+        with after.all:
+            self.shared = False
+
         # A story map generated and validated without violations is done.
         with it("should name generate on the next fidelity as the next action"):
             expect(next_action_of(self.project.ticket_json("sign-up"))).to(equal("generate"))
@@ -836,13 +854,11 @@ with description("the board tools") as self:
 
     # (S) Person --> Send Next Fidelity Action
     with context("with a ticket whose next fidelity has violations"):
-        with before.each:
-            self.project.ticket(
-                "sign-up",
-                "2026-10-31T01:00:00Z generate /work stories story_map markdown stories no-chat",
-                "2026-10-31T01:00:01Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
-                title="Sign up",
-            )
+        with before.all:
+            self.shared, self.project = True, _with_violations(ProjectTools())
+
+        with after.all:
+            self.shared = False
 
         with it("should name validate as the next action"):
             expect(next_action_of(self.project.ticket_json("sign-up"))).to(equal("validate"))
@@ -861,8 +877,10 @@ with description("the board tools") as self:
             with it("should count the violations of the fidelity on its ticket"):
                 expect(violation_counts_of(self.project.ticket_json("sign-up"))).to(equal({"stories-story-map": 2}))
 
+        # The report saved with its graph above left its graph in the shared project, so this one starts afresh.
         with context("with that fidelity's report saved without its graph"):
-            with before.each:
+            with before.all:
+                self.project = _with_violations(ProjectTools())
                 self.project.report("sign-up", "stories-story-map-20261031T041200")
 
             with it("should leave a fidelity with no saved graph uncounted"):
@@ -870,7 +888,11 @@ with description("the board tools") as self:
 
     # (S) Person --> Open Validation Report
     with context("with violations left on two fidelities"):
-        with before.each:
+        with after.all:
+            self.shared = False
+
+        with before.all:
+            self.shared, self.project = True, ProjectTools()
             self.project.ticket(
                 "sign-up",
                 "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
@@ -895,7 +917,11 @@ with description("the board tools") as self:
 
     # A ticket's card sits in one stage, so its violations are those of that stage's practices.
     with context("with violations left on a fidelity of a later stage"):
-        with before.each:
+        with after.all:
+            self.shared = False
+
+        with before.all:
+            self.shared, self.project = True, ProjectTools()
             self.project.ticket(
                 "sign-up",
                 "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
@@ -913,7 +939,11 @@ with description("the board tools") as self:
             expect({rule["fidelity"]["slug"] for rule in rules}).to(equal({"stories-story-map"}))
 
     with context("with violations two fidelities of one practice share in their saved graphs"):
-        with before.each:
+        with after.all:
+            self.shared = False
+
+        with before.all:
+            self.shared, self.project = True, ProjectTools()
             self.project.ticket(
                 "sign-up",
                 "2026-10-31T01:00:00Z validate Stories story_map graph-rule verb-noun-format map.md:12 no-chat",
@@ -932,7 +962,11 @@ with description("the board tools") as self:
 
     # A saved graph holds the hits of every rule of its practice, but a report answers for its own fidelity.
     with context("with a scenarios report whose saved graph holds every stories rule's hits"):
-        with before.each:
+        with after.all:
+            self.shared = False
+
+        with before.all:
+            self.shared, self.project = True, ProjectTools()
             self.project.ticket(
                 "sign-up",
                 "2026-10-31T01:00:01Z validate Stories scenarios graph-rule verb-noun-format map.md:12 no-chat",
@@ -971,7 +1005,11 @@ with description("the board tools") as self:
     # The chat bar reads the board every turn through MCP, whose answers are cut off past their size limit, so it reads
     # board.overview: the active ticket whole and every other ticket by its name and column.
     with context("with the chat bar's overview of the board"):
-        with before.each:
+        with after.all:
+            self.shared = False
+
+        with before.all:
+            self.shared, self.project = True, ProjectTools()
             for number in range(12):
                 self.project.ticket(f"ticket-{number}", *DISCOVERY_DONE, title=f"Ticket {number}")
             # The chat bar of ticket-0's own chat, which works on ticket-0.
@@ -999,6 +1037,12 @@ with description("the board tools") as self:
             expect(len(json.dumps(self.overview)) < 40_000).to(be_true)
 
     with context("that are published through the cdd server"):
+        with before.all:
+            self.shared, self.project = True, ProjectTools()
+
+        with after.all:
+            self.shared = False
+
         with it("should name each tool after its object"):
             names = set(self.project.server.tools)
             expect(names).to(equal({
```
