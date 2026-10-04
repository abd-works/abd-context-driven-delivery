/**
 * @name implement-full-interfaces
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node class
 * @id clean_engineering/model/implement-full-interfaces
 */

import javascript
import subject_filter
import model

from ThrowStmt thr, StringLiteral s, string message, AstNode contributor
where
  inSubject(thr) and
  s.getParent*() = thr and
  s.getValue().toLowerCase().matches("%not implemented%") and
  (nodeFile(thr.getFile()) or serverFile(thr.getFile()) or coreFile(thr.getFile())) and
  message = "Repository method stubs with throw new Error('not implemented')." and
  contributor = s
select s, message, contributor
