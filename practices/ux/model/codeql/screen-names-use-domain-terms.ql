/**
 * @name screen-names-use-domain-terms
 * @kind problem
 * @id cdd/practice-graph/screen-names-use-domain-terms
 * @problem.severity warning
 *
 * Connector: screen title strings in the subject vs class names in the rest of the graph.
 */

import javascript
import subject_filter
import model

from StringLiteral title
where
  inSubject(title) and
  title.getValue().matches("%Screen") and
  not exists(ClassDefinition cls |
    title.getValue().toLowerCase().matches("%" + cls.getName().toLowerCase() + "%")
  )
select title, "Screen title '" + title.getValue() + "' does not use a domain type name.", title
