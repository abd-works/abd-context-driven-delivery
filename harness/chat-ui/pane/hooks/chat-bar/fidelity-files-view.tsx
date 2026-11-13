import type { EngineInterface } from 'claude-code'

import type { FidelityFilesJson } from '../../types'
import { BRAND } from '../shared/brand'
import { openInDrawio } from './drawio-viewer-client'
import { closeFiles, isDiagram, openDesignView, openFileInEditor, openInEditorApp, showFile, validateAgain } from './fidelity-files-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The shown tab's whole text, which the pane scrolls: markdown drawn as the board and the chat draw it, with headings,
// tables and links, and any other file as its plain lines.
function FileTextView({ Box, Markdown, Text }: ElementTable, path: string, text: string) {
  return (
    <Box key="file-text" flexDirection="column">
      {path.endsWith('.md') ? <Markdown key="file-markdown" text={text} /> : text.split('\n').map((line, index) => <Text key={`line-${index}`} color={BRAND.text}>{line}</Text>)}
    </Box>
  )
}

// The shown file's path as its title: a press opens the file in the system's own editor for it.
function FileTitleView($: EngineInterface, { Button }: ElementTable, path: string) {
  return <Button key="file-title" plain label={path} onPress={() => openFileInEditor($, path)} />
}

// A diagram no one has drawn yet says so, rather than offering an empty one to open.
function DiagramNoteView({ Text }: ElementTable, shown: { path: string; exists: boolean }) {
  return <Text color={BRAND.muted}>{shown.exists ? `${shown.path} is a diagram: open it in draw.io.` : `${shown.path} is not drawn yet.`}</Text>
}

function ShownFileView($: EngineInterface, elements: ElementTable, shown: { path: string; text: string | null; exists: boolean }) {
  const { Box } = elements
  return (
    <Box key="shown-file" flexDirection="column">
      {FileTitleView($, elements, shown.path)}
      {isDiagram(shown.path) ? DiagramNoteView(elements, shown) : FileTextView(elements, shown.path, shown.text ?? '')}
    </Box>
  )
}

// A report whose saved graph predates the graph's shape says so, and offers to validate its fidelity again, as the board does.
function OutOfDateView($: EngineInterface, { Box, Button, Text }: ElementTable, slug: string) {
  return (
    <Box key="out-of-date" flexDirection="row" gap={1} alignItems="center">
      <Text color={BRAND.error}>This report's saved graph is out of date, so its graph's rules are not shown. Validate again to read them.</Text>
      <Button key="validate-again" label="Validate again" onPress={() => validateAgain($, slug)} />
    </Box>
  )
}

// The files pane: one tab per file the fidelity declares, or its validation report alone, and the shown tab's title and
// whole text.
export function FidelityFilesView($: EngineInterface, elements: ElementTable, files: FidelityFilesJson) {
  const { Box, Button, Text } = elements
  if (!files) return <Text color={BRAND.muted}>No files open.</Text>
  const shown = files.tabs.find(tab => tab.path === files.shown)
  return (
    <Box key="files" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      <Box flexDirection="row" gap={1} flexWrap="wrap">
        {files.tabs.map(tab => (
          <Button key={`file-${tab.path}`} label={tab.path.split('/').at(-1) ?? tab.path} variant={tab.path === files.shown ? 'primary' : undefined} onPress={() => showFile($, tab.path)} />
        ))}
        {shown && isDiagram(shown.path) && shown.exists ? <Button key="file-drawio" label="Open in draw.io" variant="primary" onPress={() => openInDrawio($, shown.path)} /> : null}
        {shown?.editor ? <Button key="file-editor" label={`Open in ${shown.editor}`} variant="primary" onPress={() => openInEditorApp($, shown.editor ?? '', shown.path)} /> : null}
        {files.designView ? <Button key="design-view" label="Design view" onPress={() => openDesignView($, files.designView)} /> : null}
        <Button key="files-close" label="✕" onPress={() => closeFiles($)} />
      </Box>
      {files.isOutOfDate ? OutOfDateView($, elements, files.fidelity) : null}
      {shown ? ShownFileView($, elements, shown) : <Text color={BRAND.muted}>{`${files.fidelity} declares no files.`}</Text>}
    </Box>
  )
}
