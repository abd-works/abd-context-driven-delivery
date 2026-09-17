fidelity: modules / behavior
scope: Context.partition
status: done — built

=========
theme: Context.partition
---------
ce:
Context
  partition context mode out_root
       -> index context out_root
            -> // concepts + partition_guidance
            -> // write {toolset_name}-index.md
       -> // one_go → segment; pause / index_only stop after index
       -> segment out_root
            -> // named files from index, e.g. epic-context-segment.md
  partition_guidance
       -> // module_dir/partition.md or default text
---
bdd:
a concept
  that only indexes
    it should write one {concept}-index.md
    it should not write segment files
  that partitions in one go
    it should index then segment
  that partitions with pause
    it should stop after index until the user continues
  that segments
    it should write files named from the index structure
=========
