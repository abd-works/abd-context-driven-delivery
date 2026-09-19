---
name: convert
description: >-
  Convert every supported document in folder_path to a Markdown file.
  Supported formats: .docx, .doc, .pdf, .pptx, .ppt, .txt, .md, .html, .htm.
  Writes each markdown document to folder_path/markdown/<stem>.md.
  Returns a ConversionResult containing markdown_files (absolute paths) and
  structure_notes (one StructureNote per file with heading_depth, heading_count,
  word_count).
---

Convert every supported document in folder_path to a Markdown file.
Supported formats: .docx, .doc, .pdf, .pptx, .ppt, .txt, .md, .html, .htm.
Writes each markdown document to folder_path/markdown/<stem>.md.
Returns a ConversionResult containing markdown_files (absolute paths) and
structure_notes (one StructureNote per file with heading_depth, heading_count,
word_count).

Use MCP tool: `context-setup.convert(folder_path: 'str')`
