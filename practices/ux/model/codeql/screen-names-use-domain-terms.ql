/**
 * @name screen-names-use-domain-terms
 * @practice ux
 * @fidelity
 * @node screen
 * @id ux/screen-names-use-domain-terms
 * @connection clean_engineering.class
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
