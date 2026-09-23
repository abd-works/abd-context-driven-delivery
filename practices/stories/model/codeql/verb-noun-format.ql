/**
 * @name verb-noun-format
 * @kind problem
 * @id cdd/practice-graph/verb-noun-format
 * @problem.severity warning
 */

import python
import model

from Call call, string name
where storyCall(call, name) and notVerbNounName(name)
select call, "Story name '" + name + "' is not verb-noun.", call
