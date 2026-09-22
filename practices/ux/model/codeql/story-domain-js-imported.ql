/**
 * @name story-domain-js-imported
 * @kind problem
 * @id cdd/practice-graph/story-domain-js-imported
 * @problem.severity warning
 */

import javascript
import subject_filter
import model

from ImportDeclaration imp
where inSubject(imp) and uxOnlyAdapter(imp)
select imp, "UX surface imports a stub adapter instead of story or domain JS.", imp
