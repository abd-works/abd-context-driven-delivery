/**
 * @name test-story-driven
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity acceptance_tests
 * @node module
 * @id stories/acceptance_tests/test-story-driven
 */

import javascript
import subject_filter
import model

from File f, TopLevel top, string message, AstNode contributor
where
  specFile(f) and
  f.getRelativePath().matches("%tests/%") and
  not f.getBaseName().matches("%_server.test.ts") and
  not f.getBaseName().matches("%_client.test.ts%") and
  not f.getBaseName().matches("%_e2e.spec.ts") and
  top.getFile() = f and
  inSubject(top) and
  message = "Sub-epic test file '" + f.getBaseName() + "' is missing a story-driven tier suffix." and
  contributor = top
select top, message, contributor
