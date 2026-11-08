"""The stack patterns CDD ships. Importing this package registers them with the graph's pattern overlays, so a graph
applies a pattern by its name without the framework naming it."""

from harness.graph.pattern_overlays import PatternOverlays

import cdd_guidance.practices  # noqa: F401 - the patterns build on the practices, so those are registered with them

from cdd_guidance.patterns.cdd_claude_mod.cdd_claude_mod import CddClaudeMod
from cdd_guidance.patterns.cdd_web_domain_access.cdd_web_domain_access import CddWebDomainAccess
from cdd_guidance.patterns.lern_domain_driven.lern_domain_driven import LernDomainDriven
from cdd_guidance.patterns.mern_domain_driven.mern_domain_driven import MernDomainDriven

PatternOverlays.register(CddClaudeMod, CddWebDomainAccess, LernDomainDriven, MernDomainDriven)
