/**
 * @name story-domain-js-imported
 * @practice ux
 * @fidelity mockup
 * @node screen
 * @id ux/mockup/story-domain-js-imported
 * @problem.severity warning
 * @connection stories.stories
 */

import javascript
import subject_filter
import model

from ImportDeclaration imp
where inSubject(imp) and uxOnlyAdapter(imp)
select imp, "UX surface imports a stub adapter instead of story or domain JS.", imp
