/**
 * @name pml-artifact-layout
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity acceptance_tests
 * @node module
 * @id stories/acceptance_tests/pml-artifact-layout
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(File f, TopLevel top |
    f.getBaseName().regexpMatch(".*_story\\.(ts|spec\\..*)") and
    not f.getBaseName().regexpMatch(".*_story\\.test\\..*") and
    top.getFile() = f and
    inSubject(top) and
    subject = top and
    contributor = top and
    message =
      "Story file '" + f.getBaseName() +
        "' uses legacy naming. Use {slug}.story.shared.ts, {slug}.story.domain.spec.ts, or {slug}.story.server.spec.ts."
  )
  or
  exists(Function helper, File spec |
    spec = helper.getFile() and
    spec.getBaseName().regexpMatch(".*\\.story\\.(domain|server)\\.spec\\.ts") and
    helper.getName().regexpMatch(".*(With|seed).*") and
    inSubject(helper) and
    subject = helper and
    contributor = helper and
    message =
      "Helper '" + helper.getName() +
        "' is declared in the spec. Move shared seeds to examples/ beside the data they set up."
  )
select subject, message, contributor
