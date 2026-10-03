/**
 * @name implement-full-interfaces
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity code
 * @node class
 * @id clean_engineering/code/implement-full-interfaces
 */

import javascript
import subject_filter
import model

from StringLiteral s, string message, AstNode contributor
where
  inSubject(s) and
  s.getValue().toLowerCase().matches("%not implemented%") and
  message = "Repository method stubs with throw new Error('not implemented')." and
  contributor = s
select s, message, contributor
