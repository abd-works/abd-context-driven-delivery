/**
 * @name domain views
 * @kind problem
 * @id cdd/lern/ddd/nodes/domain-view
 */

import javascript
import lern

from Function func
where domainView(func)
select domainViewId(func), func.getName(), "DomainView", "ddd", fileOf(func),
  func.getLocation().getStartLine(), func.getLocation().getEndLine(), "implementation"
