/**
 * @name vocabulary-traces-to-domain-source
 * @kind problem
 * @id cdd/stories/rules/vocabulary-traces-to-domain-source
 */

import python
import graph_rule

from string rule, string node, string violation, Call call, string label
where
  rule = "vocabulary-traces-to-domain-source" and
  call.getFunc().(Name).getId() = "story" and
  label = call.getArg(0).(StringLiteral).getS() and
  not exists(Class cls | label.toLowerCase().matches("%" + cls.getName().toLowerCase() + "%")) and
  node = nodeId("stories", "Story", slash(call.getLocation().getFile().getRelativePath()), label) and
  violation = ruleViolation(rule, node, "Story name '" + label + "' does not trace to a domain type.")
select rule, node, violation
