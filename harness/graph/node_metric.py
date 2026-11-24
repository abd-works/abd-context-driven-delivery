"""One metric of a node: a fact a limit rule of the node's practice reads, with its value and its limit, or a fact
the practice shows for information, with its value and no limit.

The explorer tree shows a node's metrics under one child of it named ``metrics``, beside the children named for its
relationship kinds, so a person sees how near a function, a class or a module is to each limit without running a
validate. A practice says which of a node's facts are metrics (``PracticeReading.metrics_of``); the graph knows no
practice's measures itself."""

from __future__ import annotations

from dataclasses import dataclass

# The name of the child of a node that its metrics sit under, which the explorer's filter offers beside the
# relationship kinds.
METRICS_GROUP = "metrics"
# The type of the entry one metric is shown as.
METRIC_TYPE = "Metric"


@dataclass(frozen=True)
class NodeMetric:
    """One fact a practice shows on a node: the name it is kept under, what a person calls it in plain English, its
    value on the node, and its limit: the most it may be, or, for a measure where higher is better (``least``), the
    least. A metric shown for information has no limit, and is never past one."""

    name: str
    label: str
    value: float | int
    limit: float | int | None = None
    least: bool = False

    @property
    def is_past_limit(self) -> bool:
        if self.limit is None:
            return False
        return self.value < self.limit if self.least else self.value > self.limit

    @property
    def said(self) -> str:
        """The metric as the tree shows it: ``lines in a function: 62, limit 50, past the limit``, or, with no limit,
        its name and its value alone: ``modules a module imports (outgoing coupling): 4``. A limit that is the least
        the value may be says so: ``limit 20 or higher``."""
        if self.limit is None:
            return f"{self.label}: {self.value:g}"
        past = ", past the limit" if self.is_past_limit else ""
        higher = " or higher" if self.least else ""
        return f"{self.label}: {self.value:g}, limit {self.limit:g}{higher}{past}"
