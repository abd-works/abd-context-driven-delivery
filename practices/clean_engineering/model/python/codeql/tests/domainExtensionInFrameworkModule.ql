/**
 * @kind problem
 * @id cdd/practice-graph/test/domainExtensionInFrameworkModule
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Class extension, Class domainType
where domainExtensionInFrameworkModule(extension, domainType)
select extension, extension.getName(), domainType
