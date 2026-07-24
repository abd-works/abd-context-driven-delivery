# Grill Answers

<!-- Fresh session — prior answers archived conceptually; grill from scratch. -->
### Partition is its own module

Chose new partition module. Owns the partition seam (outline / index / approve / materialize). Convert and chunk utilities stay behind that seam as dependencies ? not the module boundary itself.

### Partition is a Context method ? not its own module

Reversed earlier choice. partition is a method on Context (shared concept surface alongside generate/validate/?). No separate partition module. Convert/chunk remain utilities called from that method. Seam lives on the context toolset, not a new physical-folder module.

### Two Context actions ? index and segment

Chose two actions on Context, not one partition method. index produces the sections index (thin outline ? structure ? index; human approve outside). segment extracts chunks into module/epic/BC folders from an approved index. Names replace partition/materialize.

### Two Context actions ? index and segment

Chose two actions on Context, not one partition method. index produces the sections index (thin outline ? structure ? index; human approve outside). segment extracts chunks into module/epic/BC folders from an approved index. Names replace partition/materialize.

### Mother action with index + generate sub-actions

One mother action on Context orchestrates two sub-actions ? index and generate. Every @context inherits the full surface. Base behavior is simple ? read code or markdown (channel abstraction may be unnecessary). Each concept may override instructions when it needs thin/partition-specific guidance; defaults stay on base Context.

### Mother action named partition

Parent action is partition. It calls two sub-actions ? generate (thin) then index. Every @context inherits it.

### No folder layout ? named segment files from guiding structure

Drop module/epic/BC folders. After index (and approve if any), write named files from the guiding structure, e.g. epic-context-segment.md. Structure drives filenames, not directory trees.

### Partition does not call formal generate

The thin step is not Context.generate. It applies the concept plus extraction guidance to the source (code or markdown) to produce guiding structure for indexing. Formal generate stays separate; partition uses concept knowledge + extraction guidance (overridable instructions), not a generate action call.

### partition = index then segment

partition orchestrates two sub-actions. index applies concept + extraction guidance to build guiding structure / sections index. segment writes named files from that structure (e.g. epic-context-segment.md). No folders. Approve sits between index and segment if needed.

### Common guidance filename ? top-level artifacts only

Extraction guidance uses one common filename in each concept folder. File is small ? only names the top-level artifacts the concept uses to partition (not full exploration detail). Concepts override by editing that file in their folder.

### Guidance filename is partition.md

Each concept folder may hold partition.md ? small file naming top-level artifacts for indexing. Same filename everywhere; content differs per concept.

### Default partition.md guidance when missing

If a concept has no partition.md, use base default text ? determine top-level structure from user suggestion, available context, skill-provided material, etc. Do not fail. Concepts add partition.md only when they want a fixed top-level artifact list.

### Default one-go; optional pause before segment

partition defaults to index then segment in one run. User may ask to pause after index (review/approve) before segment runs.

### Index-only mode for multi-concept indexes

User may ask to scan/index only (no segment). Multiple concepts can each produce their own index over the same corpus. Default remains index+segment one-go; pause and index-only are user-requested variants.

### Index writes one file named after the concept

index does not write segment files. It produces exactly one index file, named after the concept (so multiple concepts on one corpus do not collide). segment is what writes the named structure files later.

### Index filename is concept-index.md

Index file naming pattern is {concept}-index.md ? e.g. stories-index.md when using stories. One index file per concept run.

### Partition sketch closed

Grill/sketch for Context.partition marked done. Decisions in context_tools/.context/grill-answers.md; shape in context_tools/.context/partition-sketch.md.

