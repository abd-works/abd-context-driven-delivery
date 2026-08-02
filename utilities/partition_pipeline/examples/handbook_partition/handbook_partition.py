"""Example: partition a handbook corpus into an index and verbatim segments."""

from __future__ import annotations

from partition_pipeline.partition_pipeline import PartitionPipeline


class HandbookPartition(PartitionPipeline):
    """Partition a handbook corpus: build the index then write verbatim segments."""

    def run(self, path: str) -> str:
        """Partition the handbook at *path* in one go.

        Calls ``partition`` which runs ``index`` + ``segment`` and verifies
        named-entry completeness for every produced chunk.

        Returns the action result string describing what was written.
        """
        return self.partition(context=path, mode="one_go")
