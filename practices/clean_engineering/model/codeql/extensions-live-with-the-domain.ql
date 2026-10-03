/**
 * @name extensions-live-with-the-domain
 * @practice clean_engineering
 * @fidelity modules
 * @node class
 * @id clean_engineering/modules/extensions-live-with-the-domain
 */

import python
import subject_filter
import rule_hits

from AstNode subject, string message, AstNode contributor
where graphRuleHit(subject, message, contributor, "extensions-live-with-the-domain")
select subject, message, contributor
