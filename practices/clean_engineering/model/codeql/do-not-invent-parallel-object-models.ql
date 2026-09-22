/**
 * @name do-not-invent-parallel-object-models
 * @kind problem
 * @id cdd/practice-graph/do-not-invent-parallel-object-models
 * @problem.severity warning
 *
 * Compare the subject to the rest of the graph.
 *
 * Join: a public method constructs or takes two types the rest of the graph
 * never joins.
 * Copy: same stem as a live type, no inheritance — a second type for one concept.
 * Split: stem-copies of a pair the rest of the graph keeps together, with no
 * edge between the copies.
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "do-not-invent-parallel-object-models")
select subject, message, contributor
