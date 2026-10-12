/**
 * @name lern domain views
 * @kind problem
 * @id cdd/lern/ddd/domain-view
 */

import javascript
import model

from File f, string id, string name, string file, int start, int end
where domainView(f, id, name, file, start, end)
select id, name, "DomainView", "ddd", file, start, end, "implementation"
