/**
 * @name test-story-driven
 * @practice stories
 * @pattern lern_domain_driven
 * @fidelity model
 * @node module
 * @id stories/model/test-story-driven
 */

import javascript
import subject_filter
import model

from File f, TopLevel top, string message, AstNode contributor
where
  specFile(f) and
  f.getRelativePath().matches("%tests/%") and
  not f.getBaseName().matches("%-node.test.ts") and
  not f.getBaseName().matches("%_server.test.ts") and
  not f.getBaseName().matches("%_client.test.ts%") and
  not f.getBaseName().matches("%_e2e.spec.ts") and
  not f.getBaseName().matches("%.story.%.ts") and
  not f.getBaseName().matches("%_story.test.md") and
  top.getFile() = f and
  inSubject(top) and
  message = "Sub-epic test file '" + f.getBaseName() + "' is missing a story-driven tier suffix." and
  contributor = top
select top, message, contributor
