/**
 * @name kebab-case-paths
 * @kind problem
 * @id cdd/practice-graph/kebab-case-paths
 * @problem.severity warning
 */

import javascript
import subject_filter
import model

from File file
where kebabPath(file)
select file, "Story file path is not kebab-case: " + file.getRelativePath(), file
