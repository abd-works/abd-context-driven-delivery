# What the markdown module shows

The round-6 and round-7 reviews (harness core, row 8 in round 7) counted 8 of the module's 15 classes as public (`deep-module`) and asked for *OperationProperty*, *MarkdownScope* and *MarkdownFile* to stay behind *Markdown*.

## What round 7 changed

- `markdown.py` names its seam in `__all__`, so `from harness.markdown import *` no longer hands out the classes that locate and read one file (*AssetLocation*, *AssetLocator*, *MarkdownFile*, *YamlFields*, *ExtractedMarkdown*).
- *MarkdownFile* is no longer used outside the module: the installer reads a file's settings with `FrontMatter.of_file(path)`, the one reader of a settings block, and `MarkdownFile.front_matter` is deleted.

## What stays public, and why

- ***MarkdownScope*** is how an owner hands its markdown where to look (`markdown_scope`: folder, slug, fidelity, format). The guidance module builds one for each practice and fidelity, because only the owner knows its fidelity and format; taking it out of the seam would send the module back to asking owners for their attributes, which round 5 removed.
- ***OperationProperty*** is the one way a property is made from an operation with an empty body. `@collect` in harness/agent_tools builds its properties with it, as `@markdown` and `@markdownCollection` do here, so the three annotations make properties the same way.
- *Markdown*, *MarkdownCollection*, *MarkdownText*, *HTML*, *FrontMatter*, *Format* and the two annotations are what callers read markdown through.

## harness/process

The process module's card already states its seam as a toolkit: each class is a small tool for one job on this computer that its callers use directly, so a deep-module count reads its purpose. Nothing changes there.
