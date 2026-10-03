/**
 * @name story-domain-js-imported
 * @practice ux
 * @fidelity mockup
 * @node screen
 * @id ux/mockup/story-domain-js-imported
 * @connection stories.stories
 */

import python
import subject_filter
import model

from Import imp
where inSubject(imp) and uxOnlyAdapter(imp)
select imp, "UX surface imports a stub adapter instead of story or domain JS.", imp
