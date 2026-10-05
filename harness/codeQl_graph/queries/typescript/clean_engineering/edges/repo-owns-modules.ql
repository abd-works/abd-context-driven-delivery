/**
 * @name repo-owns-modules
 * @kind problem
 * @id cdd/ce/edges/repo-owns-modules
 */

import javascript
import clean_engineering.ce

from string parent, string child, string mod
where subjectModule(mod) and parent = practiceId() and child = moduleId(mod)
select parent, child, "owns", 2, "direct" order by parent, child
