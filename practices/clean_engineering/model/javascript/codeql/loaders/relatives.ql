/**
 * @name Practice graph relatives
 * @kind problem
 * @id cdd/practice-graph/relatives
 */

import javascript
import subject_filter
import members

from string className, string name, string base, int start, string path, int end, string hint
where classProperty(className, name, base, start, path, end, hint) and isRelativeHint(hint)
select className, name, base, start, path, end, hint
